import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from scipy.optimize import least_squares
import logging

from pyH2A.Analysis.MonteCarloAnalysis import MonteCarloAnalysis, calculate_distance
from pyH2A.Utilities.find_nearest import find_nearest
from pyH2A.Utilities.input_modification import convert_input_to_dictionary, read_textfile, file_import, parse_parameter, merge
from pyH2A.Utilities.output_utilities import Figure_Lean, insert_image

def linear(
		p : np.ndarray, 
		x : np.ndarray
		) -> np.ndarray:
	'''Linear function for fitting.
	'''
	return p[0] * x + p[1]

def exponential_decline(
		p : np.ndarray, 
		x : np.ndarray
		) -> np.ndarray:
	'''Exponential decay function for fitting.
	'''
	return p[0] * np.exp(-p[1] * x)

def residual_generic(
		p : np.ndarray, 
		x : np.ndarray, 
		y : np.ndarray, 
		function : callable, 
		**kwargs : dict
		) -> np.ndarray:
	'''Generic residual function for least squares fitting.
	'''
	y_fit = function(p, x, **kwargs)
	res = y - y_fit
	return res

def fit_generic(
		x : np.ndarray, 
		y : np.ndarray, 
		function : callable, 
		p_guess : np.ndarray = None,
		kwargs : dict = {}
		) -> np.ndarray:
	'''Generic least squares fitting function.
	'''
	if p_guess is None:
		p_guess = np.ones(2)
	p = least_squares(fun=residual_generic, x0=p_guess, args=(x, y, function), kwargs = kwargs)
	return p.x

class DevelopmentDistanceTimeAnalysis:
	'''Relating development distance to time using historical data.

	Parameters
	----------
	DevelopmentDistanceTimeAnalysis > Input File > Value : str
		Path to textfile containing historical data for parameters
		specified in Monte Carlo analysis (see Notes).
	DevelopmentDistanceTimeAnalysis > Log Normalization > Value : bool
		Boolean flag to control if logarithmic normalization is used
		for distance calculation or not. If `False`, linear normalization is used.
		When analyzing historical data, it is advised to use logaritthmic 
		normalization to avoid outsized impacts of parameters which have changed on
		the order of magnitudes.
	DevelopmentDistanceTimeAnalysis > Base Year > Value : int
		Year which corresponds to the `Base` values specified in Monte Carlo analysis.
	DevelopmentDistanceTimeAnalysis > Extrapolation Limit > Year : int
		Year until which the distance/time models should be extrapolated.

	Notes
	-----
	The loaded textfile has to contain datapoints with historical parameter values for 
	the specified technology.
	The first column contains the year of the respective datapoint and the other
	columns contain the corresponding parameter values. The textfile needs to be tab 
	separated. The header of textfile has to start with `#` and needs to contain the tab separated
	column names (first being `Year` and the other being the same parameter
	names specified in the `Parameters - MonteCarloAnalysis` table.)
	If the textfile does not contain values for all parameters from the Monte Carlo analysis,
	missing parameter values are set to the base/reference value are are assumed to be 
	constant across all years included in the textfile.
	'''

	def __init__(
			self, 
			input_file : str
			) -> None:
		
		self.logger: logging.Logger = logging.getLogger("pyH2A.Analysis.DevelopmentDistanceTimeAnalysis")
		self.logger.info("Starting DevelopmentDistanceTimeAnalysis")
		# Initialize the development distance time analysis with the provided input file
		self.inp = convert_input_to_dictionary(input_file)
		self.monte_carlo = MonteCarloAnalysis(input_file)
		self.mc_parameters = deepcopy(self.monte_carlo.parameters)

		if 'Display Parameters' in self.inp:
			self.color = self.inp['Display Parameters']['Color']['Value']
			self.display_name = self.inp['Display Parameters']['Name']['Value']
		else:
			self.color = 'darkgreen'
			self.display_name = 'Model'

		if self.inp['DevelopmentDistanceTimeAnalysis']['Log Normalization']['Value'] == 'False':
			self.log_normalize = False
		else:
			self.log_normalize = True

		self.base_year = self.inp['DevelopmentDistanceTimeAnalysis']['Base Year']['Value']
		self.limit_year = self.inp['DevelopmentDistanceTimeAnalysis']['Extrapolation Limit Year']['Value']

		self.import_data(self.inp['DevelopmentDistanceTimeAnalysis']['Input File']['Value'])
		self.map_parameters()
		self.harmonize_monte_carlo_parameters()
		self.historical_development_distance()
		self.fit_historical_development_distance()

	def import_data(
			self, 
			file_name : str
			) -> None:
		'''Importing historical data from textfile.
		'''
		self.data = read_textfile(file_name, delimiter = '	')
		self.years = self.data[:,0]

		file_read = file_import(file_name, mode = 'r')

		for row_counter, line in enumerate(file_read):
			if line[0] != '#':
				break
			else:
				line_clean = line.strip(' #\n')
				column_names = parse_parameter(line_clean, delimiter = '	')

		self.column_names = column_names

	def map_parameters(
			self
			) -> None:
		'''Mapping parameters from historical data input file to Monte Carlo
		parameters.
		'''
		parameters = {}

		mapped = [False] * len(self.column_names)
		mapped[0] = True # Time column at index 0
		
		for counter, name in enumerate(self.column_names):
			if name in self.mc_parameters:
				parameters[name] = merge(self.mc_parameters[name], {'Index' : counter})
				mapped[counter] = True

		if False in mapped:
			unmapped_columns = np.asarray(self.column_names)[~np.asarray(mapped)]
			raise KeyError(f'Column(s) {unmapped_columns} could not be mapped to Monte Carlo parameters.')

		self.parameters_time = parameters

	def harmonize_monte_carlo_parameters(
			self
			) -> None:
		'''Checking if all Monte Carlo parameters are included in historical dataset.

		Notes
		-----
		If Monte Carlo parameters are missing, they are added with their
		historical value being set to the present reference/base value.
		'''
		max_column_index = len(self.column_names)

		for name, mc_parameter in self.mc_parameters.items():
			if name not in self.parameters_time:
				self.parameters_time[name] = mc_parameter
				self.parameters_time[name]['Index'] = max_column_index
				self.data = np.c_[self.data, np.ones(len(self.data)) * mc_parameter['Reference']]

				max_column_index += 1

				self.logger.info(f'{__name__} is adding {name} (set to reference value) to historical development distance analysis parameters.')

		assert sorted(list(self.parameters_time)) == sorted(list(self.mc_parameters)), 'Monte Carlo parameters differ from historical parameter data.'

	def historical_development_distance(
			self
			) -> None:
		'''Calculating development distance for historical and Monte Carlo analysis data.

		Notes
		-----
		To ensure that historical development distances are consistent with the Monte
		Carlo derived development, Monte Carlo distances are recalculated using the 
		same hyperparameters. If `log_normalize` is set to `True`, all distances
		are calculated using logarithmic normalization.
		'''
		self.distances = calculate_distance(self.data, self.parameters_time, self.monte_carlo.principal,
											metric = 'cityblock', sum_distance = True,
											log_normalize = self.log_normalize)

		self.monte_carlo.development_distance(log_normalize = self.log_normalize,
											  sum_distance = True)

		self.monte_carlo.full_distance_cost_relationship(log_normalize = self.log_normalize,
														 sum_distance = True)

	def fit_historical_development_distance(
			self
			) -> None:
		'''Linear and asymptotic models are fitted to historical distances and are used 
		to extrapolate into the future.

		Notes
		-----
		To simply fitting of the exponential/asymptotic model, year values and distances are
		transformed to start at 0 and converge to 0, respectively. Both the linear and the
		asymptotic model are then fitted to the transformed data. The results are transformed
		back for visualization.
		'''
		years_shifted = self.years - np.amin(self.years)
		distances_shifted = -self.distances + 1

		p_expo = fit_generic(years_shifted, distances_shifted, exponential_decline, p_guess = np.ones(2))
		p_linear = fit_generic(years_shifted, distances_shifted, linear, p_guess = np.ones(2))

		years_shifted_extended = np.arange(0, self.limit_year - np.amin(self.years) + 1, 1)
		years_extended = years_shifted_extended + np.amin(self.years)

		self.expo_distance_model = -exponential_decline(p_expo, years_shifted_extended) + 1
		self.linear_distance_model = -linear(p_linear, years_shifted_extended) + 1

		self.years_extended = years_extended

		self.p_expo = p_expo
		self.p_linear = p_linear

	def determine_distance_time_correspondence(
			self, 
			years : np.ndarray, 
			model : np.ndarray, 
			spacing : int = 1,
			minimum_tick_distance : float = 0.1,
			spacing_distances : np.ndarray = np.array([1, 2, 3, 5, 10, 15, 20])
			) -> tuple[np.ndarray, np.ndarray]:
		'''Mapping development distance to time for plotting.

		Parameters
		----------
		years : ndarray
			1D array of years, for which development distances have been computed
			using the specified model.
		model : ndarray
			1D array of modelled, time-dependent development distance values.
		spacing : int, optional
			Spacing of year ticks for visualization. Unit is years.
		minimum_tick_distance : float, optional
			Minimum allowable distance between year ticks in axis coordinates (0 to 1).
		spacing_distances : ndarray, optional
			Possible spacings which are to be used if specified spacing violates 
			`minimum_tick_distance`.

		Returns
		-------
		labels : ndarray
			Array of year tick labels.
		distances : ndarray
			Array of distances, to which year tick labels correspond.

		Notes
		-----
		If specified spacing leads to tick separation which is smaller than
		`minimum_tick_distance`, the spacing is increased by iterating through
		`spacing_distances` until the `minimum_tick_distance` criterion is fullfilled.
		'''

		def generate_distances(
				max_idx : int,
				label_spacing : int
				) -> tuple[np.ndarray, np.ndarray]:
			labels = np.arange(self.base_year, years[max_idx]+1, label_spacing)
			distances_idx = find_nearest(years, labels)
			distances = model[distances_idx]
			distances[0] = 0

			return labels, distances

		max_idx = np.where(model <= 1)[0][-1]
		labels, distances = generate_distances(max_idx, spacing)

		spacing_idx = 0

		while np.amin(np.diff(distances)) < minimum_tick_distance and spacing_idx < len(spacing_distances):
			labels, distances = generate_distances(max_idx, spacing_distances[spacing_idx])
			spacing_idx += 1

		return labels.astype('int'), distances

	def generate_time_axis(
			self, 
			ax : plt.Axes, 
			position : float, 
			distances : np.ndarray, 
			labels : np.ndarray, 
			axis_label : str, 
			color : str
			) -> None:
		'''Generating additional x axis for plot which maps development distance to time.
		'''
		ax.xaxis.set_ticks_position('bottom')
		ax.xaxis.set_label_position('bottom')
		ax.spines['bottom'].set_position(('axes', position))

		ax.set_xticks(distances)
		ax.set_xticklabels(labels)
		ax.set_xlabel(axis_label)

		ax.xaxis.label.set_color(color)
		ax.tick_params(axis = 'x', colors = color)
		ax.spines['bottom'].set_color(color)

	def plot_distance_histogram(
			self, 
			ax : plt.Axes = None, 
			figure_lean : bool = True,
			linear_axis_y_pos : float = -0.4,
			expo_axis_y_pos : float = -0.8,
			linear_axis_label : str = 'Year (linear model)',
			expo_axis_label : str = 'Year (asymptotic model)',
			label_kwargs : dict = {},
			hist_kwargs : dict = {}, 
			table_kwargs : dict = {}, 
			image_kwargs : dict = {}, 
			plot_kwargs : dict = {},  
			**kwargs : dict
			) -> plt.Figure:
		'''Plot distance histogram with additional axis mapping development distance
		to time.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		linear_axis_y_pos : float, optional
			y position of linear model time axis in axis coordinates.
		expo_axis_y_pos : float, optional
			y position of exponential/asymptotic model time axis in axis coordinates.
		linear_axis_label : str, optional
			String for label of linear model time axis.
		expo_axis_label : str, optional
			String for label of exponential/asymptotic model time axis.
		label_kwargs : dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Analysis.DevelopmentDistanceTimeAnalysis.DevelopmentDistanceTimeAnalysis.determine_distance_time_correspondence`.
		hist_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Analysis.MonteCarloAnalysis.MonteCarloAnalysis.plot_distance_histogram`
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.MonteCarloAnalysis.MonteCarloAnalysis.render_parameter_table`
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.
		'''

		kwargs = {**{'left': 0.2, 'right': 0.55, 'bottom': 0.5, 'top': 0.9, 'hspace': 0.2,
	 			     'fig_width': 10, 'fig_height': 2.5, 'font_size': 12,
	 			     'fig_height': 3.5,
	 			     'name': 'Distance_Time_Histogram'}, 
	 			  **kwargs, **plot_kwargs}

		table_kwargs = {**{'colWidths': [0.55, 0.25, 0.07, 0.25], 'format_cutoff': 7}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': -0.35, 'y': 0.5, 'zoom': 0.08}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		cm = plt.get_cmap('plasma')

		self.monte_carlo.plot_distance_histogram(ax = ax, figure_lean = False,
												 xlabel = True,
												 table_kwargs = table_kwargs,
												 image_kwargs = image_kwargs,
											  	 **hist_kwargs)

		labels_linear, distances_linear = self.determine_distance_time_correspondence(
																self.years_extended, 
																self.linear_distance_model,
																**label_kwargs)
		labels_expo, distances_expo = self.determine_distance_time_correspondence(
																self.years_extended, 
																self.expo_distance_model,
																**label_kwargs)

		ax1 = ax.twiny()
		ax2 = ax.twiny()

		self.generate_time_axis(ax1, linear_axis_y_pos, distances_linear, labels_linear, 
								linear_axis_label, cm(0.25))
		self.generate_time_axis(ax2, expo_axis_y_pos, distances_expo, labels_expo, 
								expo_axis_label, cm(0.0))

		if figure_lean is True:
			figure.execute()
			return figure.fig

	def plot_distance_cost_relationship(
			self, 
			ax : plt.Axes = None, 
			figure_lean : bool = True,
			linear_axis_y_pos : float = -0.25,
			expo_axis_y_pos : float = -0.5,
			linear_axis_label : str = 'Year (linear model)',
			expo_axis_label : str = 'Year (asymptotic model)',
			label_kwargs : dict = {},
			dist_kwargs : dict = {}, 
			table_kwargs : dict = {}, 
			image_kwargs : dict = {}, 
			plot_kwargs : dict = {}, 
			**kwargs : dict
			) -> plt.Figure:
		'''Plot distance/cost relationship with additional axis mapping development distance
		to time.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		linear_axis_y_pos : float, optional
			y position of linear model time axis in axis coordinates.
		expo_axis_y_pos : float, optional
			y position of exponential/asymptotic time axis in axis coordinates.
		linear_axis_label : str, optional
			String for label of linear model time axis.
		expo_axis_label : str, optional
			String for label of exponential/asymptotic model time axis.
		label_kwargs : dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Analysis.DevelopmentDistanceTimeAnalysis.DevelopmentDistanceTimeAnalysis.determine_distance_time_correspondence`.
		dist_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Analysis.MonteCarloAnalysis.MonteCarloAnalysis.plot_distance_cost_relationship`
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.MonteCarloAnalysis.MonteCarloAnalysis.render_parameter_table`
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.
		'''

		kwargs = {**{'left': 0.09, 'right': 0.5, 'bottom': 0.4, 'top': 0.95,
					 'fig_width': 9, 'fig_height': 4.5, 'font_size': 12,
					 'name': 'Distance_Cost_Time_Relationship'}, 
					 **kwargs, **plot_kwargs}

		dist_kwargs = {**{'log_scale': False, 'legend_loc': 'upper right'},
					   **dist_kwargs}

		table_kwargs = {**{'xpos': 1.05, 'ypos': 0.5, 'height': 0.5, 'edge_padding': 0.0}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': 1.6, 'y': 0.2, 'zoom': 0.095}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		cm = plt.get_cmap('plasma')

		self.monte_carlo.plot_distance_cost_relationship(ax = ax, figure_lean = False,
														 xlim = [0, 1],
														table_kwargs = table_kwargs,
														image_kwargs = image_kwargs,
														**dist_kwargs)
		labels_linear, distances_linear = self.determine_distance_time_correspondence(
																self.years_extended, 
																self.linear_distance_model,
																**label_kwargs)
		labels_expo, distances_expo = self.determine_distance_time_correspondence(
																self.years_extended, 
																self.expo_distance_model,
																**label_kwargs)

		ax1 = ax.twiny()
		ax2 = ax.twiny()

		self.generate_time_axis(ax1, linear_axis_y_pos, distances_linear, labels_linear, 
								linear_axis_label, cm(0.25))
		self.generate_time_axis(ax2, expo_axis_y_pos, distances_expo, labels_expo, 
								expo_axis_label, cm(0.0))

		if figure_lean is True:
			figure.execute()
			return figure.fig

	def plot_distance_indicator(
			self, 
			ax : plt.Axes, 
			target_distances : np.ndarray, 
			model : np.ndarray, 
			years : np.ndarray, 
			color : str, 
			ylim_lower : float
			) -> None:

		idx = find_nearest(model, target_distances)

		x = years[idx[0]:idx[1]+1]
		y = model[idx[0]:idx[1]+1]
		y_lower = np.ones(len(x)) * ylim_lower

		ax.fill_between(x, y, y_lower, color = color)

		# for i in idx:
		# 	x_coord = years[i]
		# 	y_coord = model[i]

		# 	ax.annotate('', xy = (x_coord, y_coord), 
		# 					xytext = (x_coord, ylim_lower), 
		# 					arrowprops={'arrowstyle': '-', 'ls': 'dashed', 'color': color})

	def plot_distance_time_relationship(
		self, 
		ax : plt.Axes = None, 
		figure_lean : bool = True,  
		legend_loc : str = 'upper left',
		xlabel_string : str = 'Year',
		ylabel_string : str = 'Development distance',
		expo_label_string : str = 'Asymptotic model',
		linear_label_string : str = 'Linear model',
		datapoint_label_string : str = ' historical distance',
		markersize : float = 10,
		color_future : bool = True,
		parameter_table : bool = True,
		target_distances : bool = None,
		table_kwargs : dict = {}, 
		image_kwargs : dict = {}, 
		plot_kwargs : dict = {},
		**kwargs : dict
	):
		'''Ploting relationship between time and development distance based on 
		historical data.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		legend_loc : str, optional
			Controls location of legend in plot. Defaults to 'upper left'.
		xlabel_string : str, optional
			String for x axis label.
		ylabel_string : str, optional
			String for y axis label.
		expo_label_string : str, optional
			String for label of exponential/asymptotic model.
		linear_label_string : str, optional
			String for label of linear model.
		datapoint_label_string : str, optional
			Second part of string for label of historical datapoints. The first part
			is the display name of the model.
		markersize : float, optional
			Size of markers in scatter plot.
		color_future : bool, optional
			Boolean flag to control if past or future region of plot is colored.
		parameter_table : bool, optional
			If parameter_table is True, the parameter table is shown in the plot.
		target_distances : ndarray, optional
			Target distance range as an 1D array with two entries ([lower_limit, higher_limit]),
			which is highlighted in the plot.
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.		
		'''

		kwargs = {**{'left': 0.09, 'right': 0.5, 'bottom': 0.15, 'top': 0.95,
				     'fig_width': 9, 'fig_height': 4, 'font_size': 12,
				     'name': 'Distance_Time_Relationship'}, 
				      **kwargs, **plot_kwargs}

		table_kwargs = {**{'xpos': 1.05, 'ypos': 0.5, 'height': 0.5, 'edge_padding': 0.0}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': 1.6, 'y': 0.2, 'zoom': 0.095}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		cm = plt.get_cmap('plasma')

		ax.plot(self.years_extended, self.linear_distance_model, color = cm(0.25),
				label = linear_label_string)
		ax.plot(self.years_extended, self.expo_distance_model, color = cm(0.0), 
				label = expo_label_string)
		ax.plot(self.years, self.distances, '.', color = self.color, markersize = markersize,
				label = self.display_name + datapoint_label_string)

		xlim = ax.get_xlim()
		ax.set_xlim(left = xlim[0], right = np.amax(self.years_extended))

		ylim = ax.get_ylim()
		ax.set_ylim(ylim)

		ax.axhspan(0, 1, color = cm(0.5), alpha = 0.1)

		if color_future:
			ax.axvspan(self.base_year, np.amax(self.years_extended), color = cm(0.75), alpha = 0.1)
		else:
			ax.axvspan(xlim[0], self.base_year, color = cm(0.75), alpha = 0.1)

		ax.set_xlabel(xlabel_string)
		ax.set_ylabel(ylabel_string)
		ax.legend(loc = legend_loc)

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		if parameter_table is True:
			self.monte_carlo.render_parameter_table(ax, **table_kwargs)

		if image_kwargs['path'] is not None:
			insert_image(ax = ax, **image_kwargs)

		if target_distances is not None:
			ax.axhspan(target_distances[0], target_distances[1], color = 'gray', alpha = 0.3)

			self.plot_distance_indicator(ax, target_distances, self.linear_distance_model,
										 self.years_extended, cm(0.25), ylim[0])

			self.plot_distance_indicator(ax, target_distances, self.expo_distance_model,
										 self.years_extended, cm(0.0), ylim[0])


		if figure_lean is True:
			figure.execute()
			return figure.fig


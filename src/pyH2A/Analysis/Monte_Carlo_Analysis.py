import multiprocessing
import copy
from pathlib import Path
from timeit import default_timer as timer
import numpy as np
from scipy.signal import savgol_filter
from scipy.spatial import distance as scipy_distance
from scipy.stats import norm as normal_distribution
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.transforms import Bbox

import pyH2A.Utilities.find_nearest as fn
from pyH2A.Utilities.input_modification import convert_input_to_dictionary,parse_parameter, parse_parameter_to_array, get_by_path, set_by_path, read_textfile, file_import
from pyH2A.Discounted_Cash_Flow import Discounted_Cash_Flow
from pyH2A.Utilities.output_utilities import make_bold, format_scientific, dynamic_value_formatting, insert_image, Figure_Lean

def select_non_reference_value(reference, values):
	'''Select value from values which is not the reference one.
	'''

	idx = np.invert(np.equal(values, reference))
	return values[idx][0]

def divide_into_batches(array, batch_size):
	'''Divide provided array into batches of size batch_size for parallel processing'''

	number_of_divisions = np.floor(len(array)/batch_size)
	idx = int(number_of_divisions * batch_size)

	first_part = array[:idx]
	second_part = array[idx:]

	batches = np.split(first_part, number_of_divisions)

	if second_part.size != 0:
		batches.append(second_part)

	return batches

def normalize_parameter(parameter, range_arr):
	'''Linear normalization of parameter (float or array) based on 
	range_arr (lower limit: range_arr[0],
	upper limit: range_arr[1])
	'''

	range_covered = range_arr[1] - range_arr[0]
	scaled = (parameter - range_arr[0]) / range_covered

	return scaled

def extend_limits(limits_original, extension):
	'''Extend limits_original in both directions by muliplying with extensions'''

	limits = np.copy(limits_original)

	limit_range = limits[1] - limits[0]

	limits[0] -= extension * limit_range
	limits[1] += extension * limit_range

	return limits

def coordinate_position(x_reference, x_values, y_reference, y_values):
	'''Determine correct position for base case label in `plot_colored_scatter()`.
	'''

	if x_reference - select_non_reference_value(x_reference, x_values) > 0:
		xtext = 0.85
	else:
		xtext = 0.05

	if y_reference - select_non_reference_value(y_reference, y_values) > 0:
		ytext = 0.93
	else:
		ytext = 0.1

	return xtext, ytext

class Monte_Carlo_Analysis:
	'''Monte Carlo analysis of a techno-economic model.

	Parameters 
	----------
	Monte_Carlo_Analysis > Samples > Value : int
		Number of samples for Monte Carlo analysis.
	Monte_Carlo_Analysis > Target Price Range ($) > Value : str
		Target price range for H2 specfied in the following format:
		lower value; higher value (e.g. "1.5: 1.54").
	Monte_Carlo_Analysis > Output File > Value : str, optional
		Path to location where output file containing Monte Carlo analysis
		results should be saved.
	Monte_Carlo_Analysis > Input File > Value : str, optional
		Path to location of file containing Monte Carlo analysis results that
		should be read.
	Parameters - Monte_Carlo_Analysis > [...] > Name : str
		Display name for parameter, e.g. used for axis labels.
	Parameters - Monte_Carlo_Analysis > [...] > Type : str
		Type of parameter values. If `Type` is 'value', provided values are
		used as is. If `Type` is 'factor', provided values are multiplied 
		with base value of parameter in input file.
	Parameters - Monte_Carlo_Analysis > [...] > Values : str
		Value range for parameter in Monte Carlo analysis. Specified in following
		format: upper limit; lower limit (order is irrelevant). Instead of actual values,
		'Base' or 'Reference' can be used to retrieve base value of parameter in input file
		as one of the values. E.g. 'Base; 20%'.
	Parameters - Monte_Carlo_Analysis > [...] > File Index : int, optional
		If Monte Carlo results are read from a provided input file, `File Index` for each
		parameter can be specified. `File Index` refers to the column position of each parameter
		in the read input file. This mapping allows for changing the display name and position
		of a parameter in the `Parameters - Monte_Carlo_Analysis` analysis table and still
		ensure correct mapping of the read results.

	Notes
	-----
	`Parameters - Monte_Carlo_Analysis` contains parameters which are to be varied in
	Monte Carlo Analysis. First column specifies path to parameter in input file 
	(top key > middle key > bottom key format, e.g. Catalyst > Cost per kg ($) > Value).
	Order of parameters can be changed, which for example affects the mapping onto different
	axis in `plot_colored_scatter` (first parameter is on x axis, second on y axis, etc.).
	'''

	def __init__(self, input_file):
		'''Initialization of Monte Carlo analysis.

		Notes 
		-----
		`self.inp` is generated from provided `input_file`. 
		If 'Input File' is specified in Monte_Carlo_Analysis table of`input_file`, 
		the provided file (which has to contain Monte Carlo simulation 
		data formatted as done by `save_results()` method) is read and Monte Carlo simulation
		results and corresponding parameter specification are retrieved.
		If 'Input File' is not specified, the parameters specified in `input_file` are processed 
		and used to generate Monte Carlo simulation data (using `perform_monte_carlo_multiprocessing()`), 
		which are stored in the specified 'Output File'.
		Subsequently, Monte Carlo datapoints are selected based on the specified target price range, 
		development distances are calculated and plots can be generated.
		'''

		self.inp = convert_input_to_dictionary(input_file)

		if 'Display Parameters' in self.inp:
			self.color = self.inp['Display Parameters']['Color']['Value']
			self.display_name = self.inp['Display Parameters']['Name']['Value']
		else:
			self.color = 'darkgreen'
			self.display_name = 'Model'

		if 'Input File' in self.inp['Monte_Carlo_Analysis']:
			self.read_results(self.inp['Monte_Carlo_Analysis']['Input File']['Value'])
		else:
			self.process_parameters()
			self.perform_full_monte_carlo()
			self.save_results(self.inp['Monte_Carlo_Analysis']['Output File']['Value'])

		self.check_parameter_integrity(self.results)
		self.target_price_components()
		self.determine_principal_components()
		self.generate_parameter_string_table()
		self.development_distance()
		self.full_distance_cost_relationship()

	def process_parameters(self):
		'''
		Monte Carlo Analysis parameters are read from 'Monte Carlo Analysis - Parameters' 
		in `self.inp` and processed.

		Notes
		-----
		The ranges for each parameter are defined in `Values` column as ';' seperated entries. Entries can
		either be a number, a path, or a `special_value` such as `Base` or `Reference`. If such a `special_value`
		is specified, the base value of that parameter is retrieved from `self.inp`.
		Parameter information is stored in `self.parameters` attribute.
		Based on the ranges for each parameter, random values (uniform distribution) are generated and stored
		in the `self.values` attribute.
		The target price range is read from `self.inp` file and stored in `self.target_price_range` attribute.
		'''

		monte = self.inp['Parameters - Monte_Carlo_Analysis']
		samples = self.inp['Monte_Carlo_Analysis']['Samples']['Value']

		number_parameters = len(monte)

		values = np.empty((samples, number_parameters))
		parameters = {}

		for counter, key in enumerate(monte):
			values_range = parse_parameter_to_array(monte[key]['Values'], delimiter = ';', 
													dictionary = self.inp, 
													top_key = 'Parameters - Monte_Carlo_Analysis', 
													middle_key = key, bottom_key = 'Values', 
													special_values = ['Base', 'Reference'], 
													path = key)

			values_range = values_range[np.argsort(values_range)]
			values[:,counter] = np.random.uniform(values_range[0], 
												  values_range[1], 
												  samples)

			path = parse_parameter(key)
			reference = get_by_path(self.inp, path)
		
			parameters[monte[key]['Name']] = {'Parameter': path, 'Type': monte[key]['Type'], 
											  'Values': values_range, 'Reference': reference, 
											  'Index': counter, 'Input Index': counter}
	
		self.values = values
		self.parameters = parameters
		self.target_price_range = parse_parameter_to_array(self.inp['Monte_Carlo_Analysis']['Target Price Range ($)']['Value'], 
														   delimiter = ';', 
														   dictionary = self.inp)

	def perform_h2_cost_calculation(self, values):
		'''H2 cost calculation for provided parameter values is performed.

		Parameters
		----------
		values : ndarray
			Array containing parameter variations.

		Returns
		-------
		h2_cost : ndarray
			1D array of H2 cost values for each set of parameters.

		Notes
		-----
		Performs H2 cost calulation by modifying a copy of self.inp based 
		on the provided values and `self.parameters`. The modified copy of 
		`self.inp` is then passed to `Discounted_Cash_Flow()`.
		A parameter value can be either a value replacing the existing one 
		in self.inp (Type = value) or it can be a factor hich will be multiplied 
		by the existing value.
		'''

		parameters = self.parameters
		h2_cost = []

		for value_set in values:
			input_dict = copy.deepcopy(self.inp)

			for key, parameter in parameters.items():
				set_by_path(input_dict, parameter['Parameter'], value_set[parameter['Index']], 
							value_type = parameter['Type'])

			dcf = Discounted_Cash_Flow(input_dict, print_info = False)
			h2_cost.append(dcf.h2_cost)

		return np.asarray(h2_cost)

	def perform_monte_carlo_multiprocessing(self, values, return_full_array = True):
		'''Monte Carlo analysis is performed with multiprocessing parallelization across
		all available CPUs.

		Parameters
		----------
		values : ndarray
			2D array containing parameters variations which are to be evaluated.
		return_full_array : bool, optional
			If `return_full_array` is True, the full 2D array containing parameter
			variations and H2 cost is returned. Otherwise, a 1D array containing only
			H2 cost values is returned.

		Returns
		-------
		full_array : ndarray
			2D array containing parameter variations and H2 cost values.
		h2_cost : ndarray
			1D array containing H2 costvalues.
		'''

		num_cpus = multiprocessing.cpu_count()
		pool = multiprocessing.Pool(num_cpus)

		value_batches = divide_into_batches(values, np.ceil(len(values)/num_cpus))
		
		h2_cost = pool.map(self.perform_h2_cost_calculation, value_batches)
		h2_cost = np.concatenate(h2_cost)

		if return_full_array is True:
			return np.c_[self.values, h2_cost]
		else:
			return h2_cost

	def perform_full_monte_carlo(self):
		'''Monte Carlo analysis is performed based on random parameter variations 
		in `self.values`.
		'''

		start = timer()

		self.results = self.perform_monte_carlo_multiprocessing(self.values)

		end = timer()
		print('Time Monte Carlo Multi:', end - start)

	def save_results(self, file_name):
		'''Results of Monte Carlo simulation are saved in `file_name` and a 
		formatted header is added. Contains name, parameter path, type and values range 
		from `self.parameters`.
		'''

		header_string = ''
		path_string = ''
		type_string = ''
		values_string = ''

		for key in self.parameters:
			header_string += str(key) + '	'
			path_string += str(self.parameters[key]['Parameter']) + '	'
			type_string += str(self.parameters[key]['Type']) + '	'
			values_string += str(self.parameters[key]['Values']) + '	'

		header_string += 'H2 Cost'
		complete_string = header_string + '\n' + path_string + '\n' + type_string + '\n' + values_string

		np.savetxt(Path(file_name), self.results, header = complete_string, delimiter = '	')

	def read_results(self, file_name):
		'''Reads Monte Carlo simulation results from `file_name`.

		Parameters
		----------
		file_name : str
			Path to file containing Monte Carlo simulation results.	

		Returns
		-------
		self.results : ndarray
			Array containing parameters and H2 cost for each model.
		self.parameters : dict
			Dictionary containing information on varied parameters.
		self.target_price_range : ndarray
			Selected target price range from `self.inp`.

		Notes
		-----
		Assumes formatting created by `self.save_results()`function.
		Header must contain name of parameters, path to parameters in input file, 
		type of parameter and value range.
		The header is processed to retrieve these atrribtues and stores them in `self.parameters`.
		Reference values for each parameter and target price range are read from self.inp
		The order of parameters is also read from `self.inp` and stored in `self.parameters` 
		as `Input Index`. If the name of a parameter has been changed in `self.inp` and is 
		different from the parameter stored in `file_name`, it is checked whether a `File Index`
		is specified, which allows for mapping of renamed parameter to parameter stored in 
		`File Index`. If `File Index` is specified, the existing parameter at this position 
		in `File Index` is renamed to the specified name.
		'''

		self.results = read_textfile(file_name, delimiter = '	', mode = 'r')

		parameters = {}
		column_dict = {}
		row_dict = {0: 'Key', 1: 'Parameter', 2: 'Type', 3: 'Values'}

		file_read = file_import(file_name, mode = 'r')

		for row_counter, line in enumerate(file_read):

			if line[0] != '#':
				break
			else:
				line_clean = line.strip(' #\n')
				line_split = parse_parameter(line_clean, delimiter = '	')

				for column_counter, element in enumerate(line_split):

					if row_dict[row_counter] == 'Key':
						parameters[element] = {}
						parameters[element]['Index'] = column_counter
						column_dict[column_counter] = element

					else:
						row_key = row_dict[row_counter]
						column_key = column_dict[column_counter]
						element = element.strip('[]')

						if row_key == 'Parameter':
							arr = []
							split = element.split(',')
							for i in split:
								arr.append(i.strip("' "))
							element = arr
				
						if row_key == 'Values':
							element = np.fromstring(element, sep = ' ', dtype = float)

						parameters[column_key][row_key] = element

		file_read.close()

		del parameters['H2 Cost']

		for key in parameters:
			parameters[key]['Reference'] = get_by_path(self.inp, parameters[key]['Parameter'])
		
		self.parameters = parameters
		self.target_price_range = parse_parameter_to_array(self.inp['Monte_Carlo_Analysis']['Target Price Range ($)']['Value'], delimiter = ';')

		for counter, (key, parameter) in enumerate(self.inp['Parameters - Monte_Carlo_Analysis'].items()):
			
			if parameter['Name'] in self.parameters:
				self.parameters[parameter['Name']]['Input Index'] = counter # Identical name, storing Input Index

			elif 'File Index' in parameter:   # Non-identical name, looking for File Index to map
				for self_key, self_parameter in self.parameters.items():

					sucess = False

					if self_parameter['Index'] == parameter['File Index']:
						self_parameter['Input Index'] = counter
						self.parameters[parameter['Name']] = self.parameters.pop(self_key)
						sucess = True

				if sucess is False:  # Raise error it not all parameters with different names could be mapped
					raise KeyError('Input Parameter {0} could not be mapped.'.format(key))

			else:
				raise KeyError('Difference between input parameter names and those stored in Monte Carlo File, no index for mapping specified.')

	def check_parameter_integrity(self, values):
		'''Checking that parameters in `self.results` are within 
		ranges specified in `self.parameters['Values']`.
		'''
		for name, parameter in self.parameters.items():
			results = values[:,parameter['Index']]
			
			minimum = np.amin(results)
			maximum = np.amax(results)

			assert minimum >= parameter['Values'][0], 'Minimum value of {0} ({1}) is smaller than specified range ({2}).'.format(name, minimum, parameter['Values'])
			assert maximum <= parameter['Values'][1], 'Maximum value of {0} ({1}) is larger than specified range ({2}).'.format(name, maximum, parameter['Values']) 

	def generate_parameter_string_table(self, base_string = 'Base', limit_string = 'Limit'):
		'''String of parameter table is generated, used in `self.render_parameter_table`.

		Parameters 
		----------
		base_string : str, optional
			String used to label base column.
		limit_string : str, optinal
			String used to label limit column.
		'''

		self.parameter_string = make_bold(self.display_name) + '\n'
		self.parameter_table = {'Table Data': [[make_bold(self.display_name), 
												make_bold(base_string), '', 
												make_bold(limit_string)]], 'Row Labels': []}

		for key, value in self.parameters.items():
			reference_value = dynamic_value_formatting(value['Reference'])
			limit_value = dynamic_value_formatting(select_non_reference_value(value['Reference'], 
																			  value['Values']))

			string = key + ': ' + reference_value + r'$\rightarrow$' + limit_value + '\n'
			self.parameter_string += string

			self.parameter_table['Table Data'].append([key, reference_value, 
													   r'$\longrightarrow$', limit_value])
			self.parameter_table['Row Labels'].append(key)

	def render_parameter_table(self, ax, xpos = 1.05, ypos = 0.0, height = 1.0, 
							   colWidths = [0.55, 0.25, 0.07, 0.25],
							   left_pad = 0.01, edge_padding = 0.02, 
							   fontsize = 12, base_string = 'Base',
							   limit_string = 'Limit'):
		'''Rendering table of parameters which are varied during Monte Carlo analysis.

		Parameters
		----------
		ax : matplotlib.axes
			Axes object in which parameter table is displayed.
		xpos : float, optional
			x axis position of left edge of table in axis fraction coordinates.
		ypos : float, optional
			y axis position of lower edge of table in axis fraction coordinates.
		height : float, optional
			Height of table in axis fraction coordinates (e.g. height = 0.5 meaning that
			the table has half the height of the plot).
		colWidths : list, optional
			List of length 4 with widths for each column from left to right in axis
			fraction coordinates.
		left_pad : float, optional
			Padding of the table on the left site.
		edge_padding: float, optional
			Padding of edges that are drawn.
		fontsize : float, optional
			fontsize for table.
		base_string : str, optional
			String used to label base column.
		limit_string : str, optional
			String used to label limit column.

		Notes
		-----
		Table is rendered in provided matplotlib.axes object.
		'''

		self.generate_parameter_string_table(base_string = base_string)

		bbox = [xpos, ypos, sum(colWidths), height]
		number_of_rows = len(self.parameter_table['Table Data'])
		cell_height = bbox[3] / number_of_rows

		table = ax.table(cellText = self.parameter_table['Table Data'],
						 edges = 'open',
						 bbox = bbox,
						 colWidths = colWidths,
						 cellLoc = 'left')

		for key, cell in table.get_celld().items():
			cell.get_text().set_color('black')
			if key[0] == 0 or key[1] >= 1:
				cell.get_text().set_color(self.color)

		table.auto_set_font_size(False)
		table.set_fontsize(fontsize)

		def set_pad_for_column(col, pad):
			cells = table.get_celld()
			column = [cell for cell in table.get_celld() if cell[1] == col]
			for cell in column:
				cells[cell].PAD = pad

		set_pad_for_column(col=0, pad = left_pad)

		def plot_edge(row_position, edge_padding):

			if row_position == 'last':
				y_edge = bbox[1] + edge_padding
			else:
				y_edge = bbox[1] + bbox[3] - (row_position * cell_height) + edge_padding

			table_edge = ax.annotate('', xy = (bbox[0], y_edge), 
									 xytext = (bbox[0] + bbox[2], y_edge), 
									 xycoords = ax.transAxes, textcoords = ax.transAxes, 
									 arrowprops={'arrowstyle': '-', 'color': self.color})

		plot_edge(1, edge_padding)
		plot_edge('last', 0)

	def target_price_components(self):
		'''Monte Carlo simulation results are sorted by H2 cost and the entries of 
		`self.results` with a H2 cost within the specified target price range are stored 
		in `self.target_price_data`.
		'''

		results_sorted = self.results[np.argsort(self.results[:,-1])]
		idx = fn.find_nearest(results_sorted[:,-1], self.target_price_range)
		data = results_sorted[idx[0]:idx[1]]

		self.target_price_data = data

	def determine_principal_components(self):
		'''Converting parameters to list sorted by input index.
		'''

		# placeholder for actual PCA
		# parameter/principal component class instead of dict
		# map PCs to W, X, Y, Z?

		self.principal = [None] * len(self.parameters)
		self.base_case = [None] * len(self.parameters)

		for key, parameter in self.parameters.items():
			self.principal[parameter['Input Index']] = key
			self.base_case[parameter['Index']] = parameter['Reference']

	def target_price_2D_region(self, grid_points = 15):
		'''Determining largest region spanned by first two parameters within which
		target prices can be achieved.

		Parameters
		----------
		grid_points : int, optional
			Number of grid points to determine density of grid evaluation.

		Returns
		-------
		self.target_price_2D_region : dict
			Dict of ndarrays with information of target price 2D region.

		Notes
		-----		
		Model is evaluated on grid spanned by first two parameters (density of grid is controlled by 
		grid_points), other parameters are set to limit (non-reference) values.
		Output is a dictionary (`self.target_price_2D_region`), which can be used to overlay 
		target price region onto scatter ploting using plt.contourf
		'''

		grid_axes = np.empty((2, grid_points))
		grid_idx = []

		values = np.empty((grid_points**2, len(self.parameters)))

		for key, parameter in self.parameters.items():
			if parameter['Input Index'] < 2:
				value_range = parameter['Values']

				grid_axis = np.linspace(value_range[0], value_range[1], grid_points)
				grid_axes[parameter['Input Index']] = grid_axis
				grid_idx.append([parameter['Index'], parameter['Input Index']])

			else:
				used_value = select_non_reference_value(parameter['Reference'], parameter['Values'])
				values[:,parameter['Index']] = np.ones(len(values)) * used_value

				parameter['Target Price Range'] = {}
				parameter['Target Price Range']['Range'] = self.target_price_range
				parameter['Target Price Range']['Used Value'] = used_value

		grid_values = np.meshgrid(*grid_axes)
		grid_values_ravel = np.c_[[np.ravel(i) for i in grid_values]].T

		for idx, idx_input in grid_idx:
			values[:,idx] = grid_values_ravel[:,idx_input]

		self.check_parameter_integrity(values)	

		h2_cost = self.perform_monte_carlo_multiprocessing(values, return_full_array = False)
		h2_cost_2D = np.reshape(h2_cost, (grid_points, grid_points))

		self.target_price_2D_region = {'Grid Values': grid_values, 'H2 Cost 2D': h2_cost_2D}

	def calculate_distance(self, data, parameters, selection, metric):
		'''
		Distance of datapoints to reference is calculated using the specified metric.

		Parameters
		----------
		data: ndarray
			2D array of datapoints containing parameter values for each model.
		parameters: dict
			Dictionary specifying ranges for each parameter.
		selection: list
			List of parameters names used for distance calculation.

		Returns
		-------
		distances: ndarray
			Array containing distance for each model.

		Notes
		-----
		Parameter ranges and the reference parameters are scaled to be within 
		a n-dimensional unit cube.
		Distances are normalized by the number of dimensions, so that the maximum 
		distance is always 1.
		'''

		number_of_parameters = len(selection)

		reference = []
		data_scaled = np.empty((len(data), number_of_parameters))

		for counter, key in enumerate(selection):
			range_arr = parameters[key]['Values']

			idx = parameters[key]['Index']
			data_scaled[:,counter] = normalize_parameter(data[:,idx], range_arr)
			reference.append(normalize_parameter(parameters[key]['Reference'], range_arr))

		reference_scaled = np.array([reference])

		distances = scipy_distance.cdist(data_scaled, reference_scaled, metric = metric)

		if metric is 'cityblock':
			distances = distances / number_of_parameters
		else:
			distances = distances / np.sqrt(number_of_parameters)

		return distances

	def development_distance(self, metric = 'cityblock'):
		'''Calculation of development distance for models within target price range.

		Parameters
		----------
		metric: str, optional
			Metric used for distance calculation, defaults to `cityblock`.

		Returns
		-------
		self.distances: ndarrray
			Array containing distances for models within target price range.

		Notes
		-----
		The euclidean or cityblock distance in n-dimensional space of each Monte Carlo simulation datapoint within 
		the target price range to the reference point is calculated and stored in self.distances.
		Parameter ranges and the reference parameters are scaled to be within a n-dimensional unit cube.
		Distances are normalized by the number of dimensions, so that the maximum distance is always 1.'''

		self.distances = self.calculate_distance(self.target_price_data, self.parameters, self.principal, metric = metric)

	def full_distance_cost_relationship(self, metric = 'cityblock', reduction_factor = 25, 
										poly_order = 4):
		'''Calculation of development distance for all datapoints from Monte Carlo Analysis and
		calculation of Savitzky-Golay filter.

		Parameters
		----------
		metric : str, optional
			Distance metric used for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.calculate_distance`
		reduction_factor : int, optional
			Determines window size for Savitzky-Golay filter.
		poly_order : int, optional
			Order of polynomial for Savitzky-Golay filter

		Returns
		-------
		self.results_distances_sorted : ndarray
			Sorted array of distances for all datapoints from Monte Carlo Analysis.
		self.distances_cost_savgol : ndarray
			Savitzky-Golay filter results.
		'''

		window_length = int(len(self.results)/reduction_factor)

		if window_length % 2 == 0:
			window_length += 1

		distances = self.calculate_distance(self.results, self.parameters, self.principal, metric = metric)

		results_distances = np.c_[self.results, distances]
		self.results_distances_sorted = results_distances[np.argsort(results_distances[:,-1])]

		smoothed = savgol_filter(self.results_distances_sorted[:,-2], window_length, poly_order)
	
		self.distances_cost_savgol = np.c_[self.results_distances_sorted[:,-1], smoothed]

	def plot_complete_histogram(self, bins = None, xlim_low = None, xlim_high = None,
								xlabel_string = 'Levelized $H_{2}$ Cost / \$/kg', 
								ylabel_string = 'Normalized Frequency',
								image_kwargs = {}, plot_kwargs = {},
								**kwargs):
		'''Complete histogram of price distribution from Monte Carlo analysis

		Parameters 
		----------
		bins : int, optional
			Number of bins for histogram. If `None`, bins is calculated
			from the size of `self.results`.
		xlim_low : float or None, optional
			Lower x axis limit.
		xlim_high : float or None, optional
			Higher x axis limit.
		xlabel_string : str, optional
			String for x axis label.
		ylabel_string : str, optional
			String for y axis label.
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
			matplotlib.fig is returned.
		'''

		kwargs = {**{'right': 0.95, 'bottom': 0.15, 'top': 0.95,
	 			     'fig_width': 7, 'fig_height': 4, 'font_size': 12,
	 			     'name': 'Monte_Carlo_Complete_Histogram'}, 
	 			  **kwargs, **plot_kwargs}

		image_kwargs = {**{'path': None, 'x': 0.5, 'y': 0.8, 'zoom': 0.08}, 
						**image_kwargs}

		figure = Figure_Lean(**kwargs)
		ax = figure.ax

		if bins is None:
			bins = int(len(self.results) / 20)

		ax.hist(self.results[:,-1], bins = bins, density=True, color=self.color, edgecolor = 'black')

		ax.set_xlabel(xlabel_string)
		ax.set_ylabel(ylabel_string)

		if xlim_low is not None:
			ax.set_xlim(xlim_low, xlim_high)

		if image_kwargs['path'] is not None:
			insert_image(ax = ax, **image_kwargs)

		figure.execute()

		return figure.fig

	def plot_colored_scatter(self, limit_extension = 0.03,   
							 title_string = 'Target Price Range: ', 
							 base_string = 'Base',
							 image_kwargs = {}, plot_kwargs = {},  
							 **kwargs):
		'''Plotting colored scatter plot showing all models within target price range.

		Parameters
		----------
		limit_extension: float, optional
			Amount of limit extension of axes as fraction of axis range.
		title_string : str, optional
			String for title.
		base_string : str, optional
			String to label base case datapoint.
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
			matplotlib.fig is returned.

		Notes
		-----
		x, y and color axis are determined by 
		:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.determine_principal_components`,
		with pc[0] being the x axis, pc[1] the y axis and pc[2] the color axis. Order can
		be changed by changing order of parameters in input file.
		'''

		kwargs = {**{'left': 0.15, 'right': 0.9, 'bottom': 0.11, 'top': 0.88,
	 			     'fig_width': 6.4, 'fig_height': 4.8, 'font_size': 12,
	 			     'name': 'Monte_Carlo_Colored_Scatter'}, 
	 			  **kwargs, **plot_kwargs}

		image_kwargs = {**{'path': None, 'x': 0.5, 'y': 0.8, 'zoom': 0.08}, 
						**image_kwargs}

		pc = self.principal
		par = self.parameters

		figure = Figure_Lean(**kwargs)
		ax = figure.ax
		fig = figure.fig

		cm = plt.get_cmap('plasma')

		self.target_price_2D_region()

		contour_fill = ax.contourf(*self.target_price_2D_region['Grid Values'], 
							        self.target_price_2D_region['H2 Cost 2D'],
							        levels = [0., max(self.target_price_range)], 
							        		  alpha = 0.1, colors = [cm(0.0)])

		base_case_h2_cost_appended = np.r_[self.base_case, 0]
		target_price_data_appended = np.vstack((self.target_price_data, 
												base_case_h2_cost_appended))

		scatter = ax.scatter(target_price_data_appended[:,par[pc[0]]['Index']], 
							 target_price_data_appended[:,par[pc[1]]['Index']], 
						 c = target_price_data_appended[:,par[pc[2]]['Index']], 
						 	 cmap = 'plasma', alpha = 1.)

		colorbar = fig.colorbar(scatter, ax=ax)

		ax.set_xlim(extend_limits(par[pc[0]]['Values'], limit_extension))
		ax.set_ylim(extend_limits(par[pc[1]]['Values'], limit_extension))
		scatter.set_clim(par[pc[2]]['Values'])

		ax.set_xlabel(pc[0])
		ax.set_ylabel(pc[1])
		colorbar.set_label(pc[2])

		xtext, ytext = coordinate_position(par[pc[0]]['Reference'], par[pc[0]]['Values'],
										   par[pc[1]]['Reference'], par[pc[1]]['Values']) 

		ax.annotate(make_bold(base_string), xy = (par[pc[0]]['Reference'], 
					par[pc[1]]['Reference']), xytext = (xtext, ytext), 
					textcoords = 'axes fraction')

		ax.set_title(make_bold(title_string) + '{0} - {1} \$/kg'.format(
											self.target_price_range[0], 
											self.target_price_range[1]))

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		if image_kwargs['path'] is not None:
			insert_image(ax = ax, **image_kwargs)

		figure.execute()

		return figure.fig

	def plot_colored_scatter_3D(self, limit_extension = 0.03,   
							 	title_string = 'Target Price Range: ',
							 	**kwargs):
		'''3D colored scatter plot of models within target price range.
	
		Parameters
		----------
		limit_extension: float, optional
			Amount of limit extension of axes as fraction of axis range.
		title_string: str, optional
			Title string.

		Returns
		-------
		fig: matplotlib.figure
			Figure object.
		'''
		from mpl_toolkits.mplot3d import Axes3D
	
		pc = self.principal
		par = self.parameters

		fig = plt.figure()
		ax = Axes3D(fig, auto_add_to_figure=False)
		fig.add_axes(ax)

		scatter = ax.scatter(self.target_price_data[:,par[pc[0]]['Index']], 
							 self.target_price_data[:,par[pc[1]]['Index']],  
							 self.target_price_data[:,par[pc[3]]['Index']], 
							 c = self.target_price_data[:,par[pc[2]]['Index']], 
							 cmap = 'plasma', depthshade = False)
	
		colorbar = fig.colorbar(scatter, ax=ax, shrink = 0.9)

		ax.set_xlim(extend_limits(par[pc[0]]['Values'], limit_extension))
		ax.set_ylim(extend_limits(par[pc[1]]['Values'], limit_extension))
		ax.set_zlim(extend_limits(par[pc[3]]['Values'], limit_extension))
		scatter.set_clim(par[pc[2]]['Values'])

		ax.set_xlabel(pc[0])
		ax.set_ylabel(pc[1])
		ax.set_zlabel(pc[3])
		colorbar.set_label(pc[2])

		ax.set_title(make_bold(title_string) + '{0} - {1} \$/kg'.format(
											self.target_price_range[0], 
											self.target_price_range[1]))
	
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		plt.show()

		return fig

	def plot_distance_histogram(self, ax = None, bins = 25, 
								figure_lean = True, xlabel = False, title = True,
								xlabel_string = 'Normalized Distance',
								ylabel_string = 'Frequency',
								title_string = 'Target Price Range',
								table_kwargs = {}, image_kwargs = {}, plot_kwargs = {},
								 **kwargs):

		'''Plotting development distances as histogram.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		bins : int, optional
			Number of bins for histogram.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		xlabel : bool, optional
			Flag to control if x axis label is displayed or not.
		title : bool, optional
			Flag to control if title is displayed or not.
		x_label_string : str, optional
			String for x axis label.
		y_label_string : str, optional
			String for y axis label.
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.render_parameter_table`
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

		kwargs = {**{'left': 0.2, 'right': 0.55, 'bottom': 0.25, 'top': 0.85, 'hspace': 0.2,
	 			     'fig_width': 11, 'fig_height': 2.5, 'font_size': 12,
	 			     'name': 'Monte_Carlo_Distance_Histogram'}, 
	 			  **kwargs, **plot_kwargs}

		table_kwargs = {**{'colWidths': [0.55, 0.25, 0.07, 0.25]}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': -0.35, 'y': 0.5, 'zoom': 0.08}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		if title is True:
			ax.title.set_text(title_string + ' {0} - {1} \$/kg'.format(self.target_price_range[0], 
																       self.target_price_range[1]))

		yhist, xhist, rectangle = ax.hist(self.distances, bins = bins, density=False, 
										  color=self.color, edgecolor = 'black')
		density = np.sum(np.diff(xhist) * yhist)
	
		mu, std = normal_distribution.fit(self.distances)

		ax.set_xlim(0, 1)
		xmin, xmax = plt.xlim()
		x = np.linspace(xmin, xmax, 500)
		p = normal_distribution.pdf(x, mu, std)
		ax.plot(x, p * density, 'k', linewidth=2)

		if xlabel:
			ax.set_xlabel(xlabel_string)
		ax.set_ylabel(ylabel_string)

		if image_kwargs['path'] is not None:
			insert_image(ax = ax, **image_kwargs)

		self.render_parameter_table(ax, **table_kwargs)
	
		if figure_lean is True:
			figure.execute()
			return figure.fig
								
	def plot_distance_cost_relationship(self, ax = None, ylim = None, figure_lean = True, 
										parameter_table = True, 
	 									legend_loc = 'upper left',
	 									log_scale = False, 
	 									xlabel_string = 'Normalized Distance',
	 									ylabel_string = r'Levelized $H_{2}$ Cost / \$/kg',
	 									table_kwargs = {}, image_kwargs = {}, plot_kwargs = {},
	 									**kwargs):
		'''Plotting relationship of development distance and H2 cost.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		ylim : float, optional
			Limit value for y axis, deactivated when log scale is used. Deafault is None.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		parameter_table : bool, optional
			If parameter_table is True, the parameter table is shown in the plot.
		legend_loc : str, optional
			Controls location of legend in plot. Defaults to 'upper left'.
		log_scale : bool, optional
			If log_scale is True, the y axis will use a log scale.
		x_label_string : str, optional
			String for x axis label.
		y_label_string : str, optional
			String for y axis label.
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.render_parameter_table`
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

		kwargs = {**{'left': 0.1, 'right': 0.9, 'bottom': 0.1, 'top': 0.95,
	 			     'fig_width': 7, 'fig_height': 4, 'font_size': 12,
	 			     'name': 'Monte_Carlo_Distance_Cost_Relationship'}, 
	 			  **kwargs, **plot_kwargs}

		table_kwargs = {**{'xpos': 1.4, 'height': 0.23, 'edge_padding': 0.0}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': 0.5, 'y': 0.8, 'zoom': 0.08}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		ax.plot(self.results_distances_sorted[:,-1], self.results_distances_sorted[:,-2], '.', 
				markersize = 1, color = self.color, alpha = 0.2)
		ax.plot(self.distances_cost_savgol[:,0], self.distances_cost_savgol[:,1], color = self.color, 
			label = self.display_name)

		if log_scale:
			ax.set_yscale('log')
			fmt = mticker.StrMethodFormatter("{x:g}")
			ax.yaxis.set_major_formatter(fmt)
		else:
			if ylim is not None:
				ax.set_ylim(0.1, ylim)

		ax.set_xlabel(xlabel_string)
		ax.set_ylabel(ylabel_string)
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)
		ax.legend(loc = legend_loc)

		if parameter_table is True:
			self.render_parameter_table(ax, **table_kwargs)

		if image_kwargs['path'] is not None:
			insert_image(ax = ax, **image_kwargs)

		if figure_lean is True:
			figure.execute()
			return figure.fig


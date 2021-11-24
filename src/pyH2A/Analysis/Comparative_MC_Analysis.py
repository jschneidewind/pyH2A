import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pyH2A.Analysis.Monte_Carlo_Analysis import Monte_Carlo_Analysis
from pyH2A.Utilities.input_modification import convert_input_to_dictionary
from pyH2A.Utilities.output_utilities import insert_image, Figure_Lean

class Comparative_MC_Analysis:
	'''Comparison of Monte Carlo analysis results for different models.

	Parameters
	----------
	Comparative_MC_Analysis > [...] > Value : str
		Path to input file for model.
	Comparative_MC_Analysis > [...] > Image : str, optional
		Path to image for model.

	Notes
	-----
	First column of `Comparative_MC_Analysis` table can include arbitrary 
	name for model.
	'''

	def __init__(self, input_file):
		self.inp = convert_input_to_dictionary(input_file)
		self.models = self.get_models()
		self.check_target_price_range_consistency()

	def get_models(self):
		'''Get models which are to be compared from `Comparative_MC_Analysis` 
		table in input file and perform Monte Carlo analysis for them.
		'''

		models = {}

		for key, input_file in self.inp['Comparative_MC_Analysis'].items():
			model = Monte_Carlo_Analysis(input_file['Value'])

			models[key] = {}
			models[key]['Model'] = model

			try:
				models[key]['Image'] = input_file['Image']
			except KeyError:
				pass

		return models

	def check_target_price_range_consistency(self):
		'''Check that the same target price ranges are specified
		for all models which are to be compared.
		'''

		model_keys = list(self.models)

		target_price_range = np.asarray(self.models[model_keys[0]]['Model'].target_price_range)
		for model_key in model_keys[1:]:
			model_range = self.models[model_key]['Model'].target_price_range
			assert np.array_equal(target_price_range, model_range), 'Target price ranges differ between input files. Reference: {0}, model: {1}'.format(target_price_range, model_range)

	def plot_comparative_distance_histogram(self, ax = None, figure_lean = True, 
											table_kwargs = {}, image_kwargs = {}, 
											plot_kwargs = {}, hist_kwargs = {},
										    **kwargs):
		'''Plot comparative development distance histogram.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.render_parameter_table`
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		hist_kwargs: dict, optional
			Dictionary containg optional keyword arguments for
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.plot_distance_histogram`
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.
		'''

		model_number = len(self.models)

		kwargs = {**{'left': 0.2, 'right': 0.55, 'bottom': 0.15, 'top': 0.9, 'hspace': 0.2,
	 				 'nrows': model_number, 'ncols': 1,	'sharex': True,	     
	 			     'fig_width': 11, 'fig_height': 1.7 * model_number, 
	 			     'font_size': 12,
	 			     'name': 'Monte_Carlo_Comparative_Distance_Histogram'}, 
	 			  **kwargs, **plot_kwargs}

		table_kwargs = {**{'colWidths': [0.55, 0.25, 0.07, 0.25]}, 
						**table_kwargs}

		image_kwargs = {**{'path': None, 'x': -0.35, 'y': 0.5, 'zoom': 0.08}, 
						**image_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		for counter, (model_name, model) in enumerate(self.models.items()):
			if counter == 0:
				show_title = True
				show_xlabel = False

			elif counter == model_number - 1:
				show_title = False
				show_xlabel = True

			else:
				show_title = False
				show_xlabel = False

			model['Model'].plot_distance_histogram(ax = ax[counter], 
											       figure_lean = False, 
												   xlabel = show_xlabel, 
												   title = show_title,
												   table_kwargs = table_kwargs,
												   **hist_kwargs)

			if 'Image' in model:
				image_kwargs['path'] = model['Image']
				insert_image(ax = ax[counter], **image_kwargs)

		if figure_lean is True:
			figure.execute()
			return figure.fig

	def plot_comparative_distance_cost_relationship(self, ax = None, figure_lean = True,
													target_line = 1.5, 
													table_kwargs = {}, image_kwargs = {}, 
											        plot_kwargs = {}, dist_kwargs = {},
													**kwargs):
		'''Plot comparative development distance/H2 cost relationship.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		target_line : float, optional
			y axis coordinate of target price line.
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.render_parameter_table`
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		dist_kwargs: dict, optional
			Dictionary containg optional keyword arguments for
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.plot_distance_cost_relationship`
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.
		'''

		model_number = len(self.models)

		kwargs = {**{'right': 0.43, 'left': 0.08, 'top': 0.92,
	 			     'fig_width': 10, 'fig_height': 6, 
	 			     'font_size': 12,
	 			     'name': 'Monte_Carlo_Comparative_Distance_Cost_Relationship'}, 
	 			  **kwargs, **plot_kwargs}

		image_kwargs = {**{'path': None, 'x': 1.2, 'y': 0.5, 'zoom': 0.08}, 
						**image_kwargs}

		dist_kwargs = {**{'log_scale': False, 'ylim': 8, 'legend_loc': 'upper right'},
					   **dist_kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		ax.plot([0, 1], [target_line, target_line], '--', color = 'black')

		for counter, (model_name, model) in enumerate(self.models.items()):
			ycoord = 1 - 1.1 * (counter / model_number) - 0.23

			table_kwargs['ypos'] = ycoord

			model['Model'].plot_distance_cost_relationship(ax = ax, figure_lean = False, 
														   table_kwargs = table_kwargs,
														   **dist_kwargs)

			if 'Image' in model:
				image_kwargs['path'] = model['Image']
				image_kwargs['y'] = ycoord + 0.12
				insert_image(ax = ax, **image_kwargs)

		if figure_lean is True:
			figure.execute()
			return figure.fig

	def plot_combined_distance(self, fig_width = 12, fig_height = 2,
							   target_line = 1.5,
							   table_kwargs = {}, image_kwargs = {}, 
							   plot_kwargs = {}, dist_kwargs = {},
							   hist_kwargs = {}, **kwargs):
		'''Plot combining development distance histogram and distance/H2 cost
		relationship.

		Parameters
		----------
		fig_width : float, optional
			Width of figure in inches.
		fig_height : float, optional
			Height of figure per model in inches.
		target_line : float, optional
			y axis coordinate of target price line.
		table_kwargs : dict, optional
			Dictionary containing optional keyword arguments for 
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.render_parameter_table`
		image_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.insert_image`
		plot_kwargs: dict, optional
			Dictionary containing optional keyword arguments for
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`, has priority over `**kwargs`.
		dist_kwargs: dict, optional
			Dictionary containg optional keyword arguments for
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.plot_distance_cost_relationship`
		hist_kwargs: dict, optional
			Dictionary containg optional keyword arguments for
			:func:`~pyH2A.Analysis.Monte_Carlo_Analysis.Monte_Carlo_Analysis.plot_distance_histogram`
		**kwargs: 
			Additional `kwargs` passed to 
			:func:`~pyH2A.Utilities.output_utilities.Figure_Lean`

		Returns 
		-------
		figure : matplotlib.fig or None
			matplotlib.fig is returned if `figure_lean` is True.
		'''

		model_number = len(self.models)

		kwargs = {**{'right': 0.675, 'left': 0.04, 'bottom': 0.15, 'top': 0.9,
				     'hspace': 0.2, 'wspace': 0.62,
	 			     'name': 'Monte_Carlo_Combined_Plot'}, 
	 			  **kwargs, **plot_kwargs}

		image_kwargs = {**{'x': -0.4}, 
						**image_kwargs}

		dist_kwargs = {**{'log_scale': False, 'ylim': 8, 'legend_loc': 'upper right'},
					   **dist_kwargs}

		gs = gridspec.GridSpec(model_number, 2)

		fig = plt.figure(figsize = (fig_width, fig_height * model_number))
		ax0 = plt.subplot(gs[:, 0])

		ax_hist = []
		for i in range(model_number):
			ax_hist.append(plt.subplot(gs[i, 1]))

		figure = Figure_Lean(provided_figure_and_axis = (fig, ax0), **kwargs)

		for model_name, model in self.models.items():
			model['Model'].plot_distance_cost_relationship(figure_lean = False, ax = ax0 ,
														   parameter_table = False,
														   **dist_kwargs)
		
		self.plot_comparative_distance_histogram(figure_lean = False, ax = ax_hist, 
											     table_kwargs = table_kwargs,
											     image_kwargs = image_kwargs,
											     hist_kwargs = hist_kwargs)

		ax0.plot([0, 1], [target_line, target_line], '--', color = 'black')

		ax0.text(-0.16, 1.04, 'A', transform=ax0.transAxes, size = 24, weight='bold')
		ax0.text(1.36, 1.04, 'B', transform=ax0.transAxes, size = 24, weight='bold')

		figure.execute()

		return fig

	
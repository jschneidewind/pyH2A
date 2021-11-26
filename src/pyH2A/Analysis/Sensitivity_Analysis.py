import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pyH2A.Discounted_Cash_Flow import Discounted_Cash_Flow
from pyH2A.Utilities.input_modification import num, convert_input_to_dictionary, parse_parameter, get_by_path, set_by_path
from pyH2A.Utilities.output_utilities import make_bold, Figure_Lean

class Sensitivity_Analysis:
	'''Sensitivity analysis for multiple parameters.

	Parameters
	----------
	Sensitivity_Analysis > [...] > Name : str
		Display name for parameter, e.g. used for plot labels.
	Sensitivity_Analysis > [...] > Type : str
		Type of parameter values. If `Type` is 'value', provided values are
		used as is. If `Type` is 'factor', provided values are multiplied 
		with base value of parameter in input file.
	Sensitivity_Analysis > [...] > Values : str
		Value pair to be used for sensitivity analysis. One value should 
		be higher than the base value, the other should be lower.
		Specified in following format: value A; value B (order is irrelevant).
		E.g. '0.3; 10'.

	Notes
	-----
	`Sensitivity_Analysis` contains parameters which are to be varied in
	sensitivity analysis. First column specifies path to parameter in input file 
	(top key > middle key > bottom key format, e.g. Catalyst > Cost per kg ($) > Value).
	Order of parameters is not relevant.
	'''

	def __init__(self, input_file):
		self.inp = convert_input_to_dictionary(input_file)
		self.base_case = Discounted_Cash_Flow(input_file, print_info = False)
		self.results = self.perform_sensitivity_analysis()

	def perform_sensitivity_analysis(self):
		'''Perform sensitivity analysis.
		'''

		sensitivity_results = {}

		for key in self.inp['Sensitivity_Analysis']:
			parameters = parse_parameter(key)
			name = self.inp['Sensitivity_Analysis'][key]['Name']

			sensitivity_results[name] = {}
			sensitivity_results[name]['Base'] = get_by_path(self.inp, parameters)
			sensitivity_results[name]['Values'] = {}

			values = parse_parameter(self.inp['Sensitivity_Analysis'][key]['Values'], 
									 delimiter = ';')

			for value in values:
				input_dict = copy.deepcopy(self.inp)
				numerical_value = num(value)
				value_type = self.inp['Sensitivity_Analysis'][key]['Type']

				set_by_path(input_dict, parameters, numerical_value, 
							value_type = value_type)

				if self.inp['Sensitivity_Analysis'][key]['Type'] == 'factor':
					sensitivity_results[name]['Base'] = '1.0x'
					shown_value = '{0}x'.format(numerical_value)
				else:
					shown_value = value
					if '%' in shown_value:
						sensitivity_results[name]['Base'] = '{0}%'.format(get_by_path(self.inp, 
																					  parameters) * 100)

				dcf = Discounted_Cash_Flow(input_dict, print_info = False)

				sensitivity_results[name]['Values'][shown_value] = dcf.h2_cost

		return sensitivity_results

	def sort_h2_cost_values(self, data):
		'''Sort H2 cost values.
		'''

		for key in data:
			values = data[key]['Values']

			low_key = min(values, key = values.get)
			high_key = max(values, key = values.get)

			data[key]['Low - Name'] = low_key
			data[key]['Low - Value'] = values[low_key]

			data[key]['High - Name'] = high_key
			data[key]['High - Value'] = values[high_key]

			del data[key]['Values']

	def sensitivity_box_plot(self, ax = None, figure_lean = True,
							 height = 0.8, label_offset = 0.1, 
						     lim_extra = 0.2, plot_kwargs = {},
						     **kwargs):
		'''Plot sensitivity box plot.

		Parameters
		----------
		ax : matplotlib.axes, optional
			Axes object in which plot is drawn. Default is None, creating new plot.
		figure_lean : bool, optional
			If figure_lean is True, matplotlib.fig object is returned.
		height : float, optional
			Height of bars.
		label_offset : float, optional
			Offset for bar labels.
		lim_extra : float, optional
			Fractional increase of x axis limits.
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

		Notes
		-----
		In plot, parameters are sorted by descending cost increase magnitude.
		'''

		data = copy.deepcopy(self.results)
		self.sort_h2_cost_values(data)

		df = pd.DataFrame.from_dict(data)
		df.sort_values(by = ['High - Value'], axis = 1, 
					   na_position = 'first', inplace = True)

		kwargs = {**{'left': 0.45, 'right': 0.99, 'bottom': 0.2, 'top': 0.95,
				     'fig_width': 7.5, 'fig_height': 4,
				     'name': 'Sensitivity_Box_Plot'}, 
				  **kwargs, **plot_kwargs}
		
		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax		

		number_of_entries = len(df.columns)
		base_case = self.base_case.h2_cost

		max_value = df.loc['High - Value'].max(skipna = True)
		min_value = df.loc['Low - Value'].min(skipna = True)

		x_width = max_value - min_value
		label_offset = x_width * label_offset
		extra = x_width * lim_extra

		xlim = [min_value - extra, max_value + extra]
		ylim = [-height, number_of_entries]	

		labels = []

		for counter, key in enumerate(df):
			lower = df[key]['Low - Value']
			upper = df[key]['High - Value']

			rectangle_left = patches.Rectangle((lower, counter-height/2), 
												base_case - lower, height, 
												edgecolor = 'none', 
												facecolor = 'darkgreen')
			rectangle_right = patches.Rectangle((base_case, counter-height/2), 
												 upper - base_case, height, 
												 edgecolor = 'none', 
												 facecolor = 'darkred')

			ax.add_patch(rectangle_left)
			ax.add_patch(rectangle_right)

			ax.annotate('${:.2f}'.format(lower), xy = (lower - label_offset, counter), 
				         va = 'center', ha = 'center')
			ax.annotate('${:.2f}'.format(upper), xy = (upper + label_offset, counter), 
				         va = 'center', ha = 'center')

			labels.append('{0}\n{1}, {2}, {3}'.format(make_bold(key), 
				                                      df[key]['Low - Name'], 
				                                      df[key]['Base'], 
				                                      df[key]['High - Name']))

		ax.set_xlabel(r'Cost sensitivity / USD per kg $H_{2}$')
		ax.set_yticks(np.arange(0, number_of_entries))
		ax.set_yticklabels(labels)
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2)

		ax.set_xlim(xlim[0], xlim[1])
		ax.set_ylim(ylim[0], ylim[1])
		ax.plot((base_case, base_case), (ylim[0], ylim[1]), '--', color = 'black')

		if figure_lean is True:
			figure.execute()
			return figure.fig

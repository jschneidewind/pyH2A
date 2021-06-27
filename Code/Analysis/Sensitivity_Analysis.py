import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12
from Discounted_Cash_Flow import Discounted_Cash_Flow
from input_modification import num, convert_input_to_dictionary, parse_parameter, get_by_path, set_by_path
from output_utilities import make_bold, Figure_Lean

import pprint

class Sensitivity_Analysis:
	'''

	Sensitivity analysis for multiple entries: sensitivity parameter (specified in its own table), which is referenced by desired entries
	In sensitivity analysis, that sensitivty parameter is then varied.

	______________
	Required Input
	______________

	# Sensitivity Analysis
	
	Parameter | Name | Type | Values
	--- | --- | --- | ---
	str | str | value or factor | num (delimited by ";")

	"Parameter" is a ">" delimited string that points to a location of the input file via
	top_key > middle_key > bottom_key

	"Name" is the parameter name displayed in the output plot.

	"Type" is either 'value' or 'factor'. If Type == value, the entered "Values" are used as is.
	if Type == factor, the entered "Values" are multiplied by the location value.

	"Values" is a ";" delimited string, an arbitrary number of values can be entered, but typcically two are used for
	sensitivity analysis.	

	______________
	Output
	______________

	Sensitivity_Analysis class object with method for plot generation.

	'''

	def __init__(self, input_file, base_case = None):
		self.inp = convert_input_to_dictionary(input_file)
		self.base_case = Discounted_Cash_Flow(input_file, print_info = False)
		self.results = self.perform_sensitivity_analysis()

	def perform_sensitivity_analysis(self):

		sensitivity_results = {}

		for key in self.inp['Sensitivity_Analysis']:
			parameters = parse_parameter(key)
			name = self.inp['Sensitivity_Analysis'][key]['Name']

			sensitivity_results[name] = {}
			sensitivity_results[name]['Base'] = get_by_path(self.inp, parameters)
			sensitivity_results[name]['Values'] = {}

			values = parse_parameter(self.inp['Sensitivity_Analysis'][key]['Values'], delimiter = ';')

			for value in values:
				input_dict = copy.deepcopy(self.inp)
				numerical_value = num(value)
				value_type = self.inp['Sensitivity_Analysis'][key]['Type']

				set_by_path(input_dict, parameters, numerical_value, value_type = value_type)

				if self.inp['Sensitivity_Analysis'][key]['Type'] == 'factor':
					sensitivity_results[name]['Base'] = '1.0x'
					shown_value = '{0}x'.format(numerical_value)
				else:
					shown_value = value
					if '%' in shown_value:
							sensitivity_results[name]['Base'] = '{0}%'.format(get_by_path(self.inp, parameters) * 100)

				dcf = Discounted_Cash_Flow(input_dict, print_info = False)

				sensitivity_results[name]['Values'][shown_value] = dcf.h2_cost

		return sensitivity_results

	def sort_h2_cost_values(self, data):

		for key in data:
			values = data[key]['Values']

			low_key = min(values, key = values.get)
			high_key = max(values, key = values.get)

			data[key]['Low - Name'] = low_key
			data[key]['Low - Value'] = values[low_key]

			data[key]['High - Name'] = high_key
			data[key]['High - Value'] = values[high_key]

			del data[key]['Values']

	def sensitivity_box_plot(self, height = 0.8, label_offset = 0.1, lim_extra = 0.2, **kwargs):

		data = copy.deepcopy(self.results)
		self.sort_h2_cost_values(data)

		df = pd.DataFrame.from_dict(data)
		df.sort_values(by = ['High - Value'], axis = 1, na_position = 'first', inplace = True)
		
		fig, ax = plt.subplots(figsize = (7.5, 4))
		fig.subplots_adjust(left = 0.45, bottom = 0.2, right = 0.99, top = 0.95)

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

			rectangle_left = patches.Rectangle((lower, counter-height/2), base_case - lower, height, edgecolor = 'none', facecolor = 'darkgreen')
			rectangle_right = patches.Rectangle((base_case, counter-height/2), upper - base_case, height, edgecolor = 'none', facecolor = 'darkred')

			ax.add_patch(rectangle_left)
			ax.add_patch(rectangle_right)

			ax.annotate('${:.2f}'.format(lower), xy = (lower - label_offset, counter), va = 'center', ha = 'center')
			ax.annotate('${:.2f}'.format(upper), xy = (upper + label_offset, counter), va = 'center', ha = 'center')

			labels.append('{0}\n{1}, {2}, {3}'.format(make_bold(key), df[key]['Low - Name'], df[key]['Base'], df[key]['High - Name']))

		ax.set_xlabel(r'Cost sensitivity / USD per kg $H_{2}$')
		ax.set_yticks(np.arange(0, number_of_entries))
		ax.set_yticklabels(labels)
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2)

		ax.set_xlim(xlim[0], xlim[1])
		ax.set_ylim(ylim[0], ylim[1])
		ax.plot((base_case, base_case), (ylim[0], ylim[1]), '--', color = 'black')

		Figure_Lean(fig, 'Sensitivity_Box_Plot', **kwargs)

		return fig
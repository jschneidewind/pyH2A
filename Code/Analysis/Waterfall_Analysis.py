import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12
from Discounted_Cash_Flow import Discounted_Cash_Flow
from input_modification import convert_input_to_dictionary, parse_parameter, get_by_path, set_by_path
from output_utilities import make_bold, Figure_Lean
import pprint

class Waterfall_Analysis:
	'''
	Perform waterfall analysis to study the compounded effect of changing multiple entries of the input.
	A list of parameters to be changed is provided in the input. In the order they are provided, each 
	parameter is changed to the provided value. The relative change of introducing each change is computed,
	and the new H2 cost (compound result of applying all changes) is calculated.

	______________
	Required Input
	______________

	# Waterfall Analysis

	Parameter | Name | Type | Value | Show Percent (optional)
	--- | --- | --- | ---
	str | str | value or factor | num

	"Parameter" is a ">" delimited string that points to a location of the input file via
	top_key > middle_key > bottom_key

	"Name" is the parameter name displayed in the output plot.

	"Type" is either 'value' or 'factor'. If Type == value, the entered "Values" are used as is.
	if Type == factor, the entered "Values" are multiplied by the location value.

	"Value" is the value to which the specified parameter should be changed.

	______________
	Output
	______________

	Waterfall_Analysis class object with method for plot generation.
	'''

	def __init__(self, input_file, base_case = None):
		self.inp = convert_input_to_dictionary(input_file)
		self.base_case = Discounted_Cash_Flow(input_file, print_info = False)

		self.results = self.perform_waterfall_analysis()

	def perform_waterfall_analysis(self):

		waterfall = self.inp['Waterfall_Analysis']

		results = {}
		results['Base Case'] = {'Value': self.base_case.h2_cost}

		for i in range(len(waterfall)):
			keys = list(waterfall)[0:i+1]
			dic = {k: waterfall.get(k, None) for k in (keys)}

			self.modify_inp_run_dcf(self.inp, dic, results)

		keys = list(results)[1:] # all keys except first one (base case)

		for key in keys:
			preceding_name = results[key]['Preceding Name']
			preceding_value = results[preceding_name]['Value']
			relative_change = results[key]['Value'] - preceding_value

			results[key]['Preceding Value'] = preceding_value
			results[key]['Relative Change'] = relative_change

		return results

	def modify_inp_run_dcf(self, inp, dic, output):

		inp_modified = copy.deepcopy(inp)

		variable = dic[list(dic)[-1]]['Name']
		output[variable] = {}
		output[variable]['Previous Changes'] = {}

		for key in dic:
			parameters = parse_parameter(key)
			name = dic[key]['Name']
			value = dic[key]['Value']
			value_type = dic[key]['Type']

			base_value = get_by_path(inp_modified, parameters)

			set_by_path(inp_modified, parameters, value, value_type = value_type)

			if dic[key]['Type'] == 'factor':
				shown_value = '{0}x'.format(value)
			else:
				shown_value = self.show_percent(value, dic[key])

			output[variable]['Previous Changes'][name] = shown_value					

		dcf = Discounted_Cash_Flow(inp_modified, print_info = False)

		output[variable]['Value'] = dcf.h2_cost
		output[variable]['Shown Value'] = shown_value
		output[variable]['Base Value'] = self.show_percent(base_value, dic[key])

		try:
			output[variable]['Preceding Name'] = dic[list(dic)[-2]]['Name']
		except IndexError:
			output[variable]['Preceding Name'] = 'Base Case'

	def show_percent(self, value, dic):
	
		if 'Show Percent' in dic:
			return '{0}%'.format(value * 100)
		else:
			return value

	def waterfall_chart(self, width = 0.7, connection_width = 1.0, label_offset = 20, plot_sorted = False, figure_width = 0.5, **kwargs):

		results = self.results

		fig, ax = plt.subplots(figsize = (figure_width * len(results) + 4, 5))
		fig.subplots_adjust(left = 0.12, bottom = 0.3, right = 0.95, top = 0.95)
		cmap = plt.get_cmap('plasma')

		df = pd.DataFrame.from_dict(results)
		max_value = df.loc['Value'].max(skipna = True)

		label_offset = max_value / label_offset

		if plot_sorted is True:
			df.sort_values(by = ['Relative Change'], axis = 1, na_position = 'first', inplace = True)
		
		# with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
		# 	print(df)

		current_value = df['Base Case']['Value']

		labels = []

		for counter, i in enumerate(df):

			if i == 'Base Case':
				bar = patches.Rectangle((counter - width/2, 0), width, df[i]['Value'], edgecolor = 'none', facecolor = cmap(0.8), zorder = 5)
				ax.add_patch(bar)
				ax.plot([counter, counter], [0, df[i]['Value']], color = 'black', linewidth = 0)
				connection = ax.annotate('', xy =(counter + width/2, current_value), xytext=(counter + 1 - width/2, current_value), arrowprops={'arrowstyle': '-', 'ls': 'dashed', 'color': 'grey', 'linewidth': connection_width})

				ax.annotate('${:.2f}'.format(df[i]['Value']), xy = (counter, df[i]['Value'] + label_offset), va = 'center', ha = 'center')

				labels.append(make_bold(i).replace(' ', '\n'))

			else:
				if df[i]['Relative Change'] >= 0:
					color = 'darkred'
					y = current_value
					y_label = current_value + df[i]['Relative Change'] + label_offset
					height = df[i]['Relative Change']
					
				else:
					color = 'darkgreen'
					y = current_value + df[i]['Relative Change']
					y_label = current_value + df[i]['Relative Change'] - label_offset
					height = abs(df[i]['Relative Change'])

				x = counter - width/2
		
				bar = patches.Rectangle((x, y), width, height, edgecolor = 'none', facecolor = color, zorder = 5)
				ax.add_patch(bar)
				ax.plot([counter, counter], [current_value, current_value + df[i]['Relative Change']], color = color, linewidth = 0)
	
				ax.annotate('${:.2f}'.format(df[i]['Relative Change']), xy = (counter, y_label), va = 'center', ha = 'center', color = color)

				current_value += df[i]['Relative Change']
				connection = ax.annotate('', xy =(counter + width/2, current_value), xytext=(counter + 1 - width/2, current_value), 
										arrowprops={'arrowstyle': '-', 'ls': 'dashed', 'color': 'grey', 'linewidth': connection_width})

				labels.append(make_bold(str(df[i]['Shown Value'])) + '\n' + i.replace(' ', '\n') + '\n' + make_bold('Base:') + '\n{0}'.format(df[i]['Base Value']))

		bar = patches.Rectangle((counter+1 - width/2, 0), width, current_value, edgecolor = 'none', facecolor = cmap(0.05), zorder = 5)
		ax.add_patch(bar)
		ax.plot([counter+1, counter+1], [0, current_value], color = 'black', linewidth = 0)
		ax.annotate('${:.2f}'.format(current_value), xy = (counter+1, current_value + label_offset), va = 'center', ha = 'center')
		labels.append(make_bold('Adjusted'))

		ax.set_ylabel(r'Levelized cost / USD per kg $H_{2}$')

		ax.set_xticks(np.arange(0, len(results)+1))
		ax.set_xticklabels(labels)

		ylim = np.asarray(ax.get_ylim())
		ylim[1] += 1.2*label_offset
		ylim[0] = 0.0
		ax.set_ylim(ylim)

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		Figure_Lean(fig, 'Waterfall_Chart', **kwargs)

		return fig


def main():

	test = Waterfall_Analysis('../Input/210512_Future_PEC_Type_1.md')
	fig = test.waterfall_chart(directory = '../Output/', show = 'True')

	plt.show()



if __name__ == '__main__':
	main()
	plt.show()


		
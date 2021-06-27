import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12
from output_utilities import make_bold, millify, bottom_offset, Figure_Lean
import types
from Discounted_Cash_Flow import Discounted_Cash_Flow

class Cost_Contributions_Analysis:
	'''
	Contributions are provided as a dictionary with three components:
	'Data' containing the name and value for each contribution.
	'Total' containign the total value
	'Table Group', containing the name of overarching group of values, which are shown. 

	cost_breakdown_plot method generates plot from provided data and total.

	if the name of the contribution contains a '-', the string will be split and only the part after the
	'-' will be displayed.
	'''

	def __init__(self, input_file):
		self.base_case = Discounted_Cash_Flow(input_file, print_info = False)

		# self.contributions = contributions
		# self.data = contributions['Data']

	def cost_breakdown_plot(self, label_offset = 5.5, xaxis_label = 'Cost / USD', data = None, plugin_property = None, **kwargs):

		if data is None:
			self.contributions = self.base_case.contributions
			self.data = self.base_case.contributions['Data']
		else:
			plugin = self.base_case.plugs[data]
			self.contributions = getattr(plugin, plugin_property)
			self.data = self.contributions['Data']

		sorted_keys = sorted(self.data, key = self.data.get)
		sorted_contributions = {}

		for key in sorted_keys:
			sorted_contributions[key] = self.data[key]

		fig, ax = plt.subplots()
		fig.subplots_adjust(left = 0.4)
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)
		
		cmap = plt.get_cmap('plasma')

		label_offset = self.contributions['Total'] / label_offset

		for counter, key in enumerate(sorted_contributions):

			if '-' in key:
				name = key.split('-')[1].strip(' ')
			else:
				name = key

			value = sorted_contributions[key]

			color_value = counter / len(sorted_contributions)
			ax.barh(name, sorted_contributions[key], color = cmap(color_value), zorder = 5)
			ax.annotate(millify(value),  
				xy = (max(value, 0) + label_offset, counter), va = 'center', ha = 'center')

		ax.barh(make_bold(self.contributions['Table Group']), self.contributions['Total'], color = 'darkgreen', zorder = 5)
		ax.annotate(millify(self.contributions['Total']), xy = (self.contributions['Total'] + label_offset, len(sorted_contributions)), va = 'center', ha = 'center')

		if self.contributions['Table Group'] == 'Total cost of hydrogen':
			xaxis_label = r'Levelized cost / USD per kg $H_{2}$'

		ax.set_xlabel(xaxis_label)

		xlim = np.asarray(ax.get_xlim())
		xlim[1] += 2 * label_offset
		ax.set_xlim(xlim)
	
		ax.ticklabel_format(axis = 'x', style = 'sci', scilimits = (0,0), useMathText = True)
		ax.xaxis._update_offset_text_position = types.MethodType(bottom_offset, ax.xaxis)
		
		Figure_Lean(fig, **kwargs)

		return fig 


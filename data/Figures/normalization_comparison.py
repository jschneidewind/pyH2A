import numpy as np
import matplotlib.pyplot as plt

from pyH2A.Analysis.Monte_Carlo_Analysis import Monte_Carlo_Analysis, normalize_parameter
from pyH2A.Utilities.output_utilities import Figure_Lean

import pprint


def generate_normalized_data(parameter, plot_base, plot_limit, log_normalize):

	values = np.linspace(plot_base, plot_limit, 100)
	normalized_values = normalize_parameter(values, parameter['Reference'], 
											parameter['Limit'], 
											log_normalize = log_normalize)

	return values, normalized_values

def plot_normalized_data(ax, parameter, plot_base, plot_limit, log_normalize,
						 name, color, label):

	values, normalized_values = generate_normalized_data(parameter, plot_base,
														 plot_limit, log_normalize)


	ax.plot(values, normalized_values, label = label, color = color)
	ax.set_xlabel(name)
	ax.set_ylabel('Normalized value')
	ax.legend()

	ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

def plot_normalization(parameters, **kwargs):

	kwargs = {**{'fig_width': 8.5, 'fig_height': 4,
			     'left': 0.08, 'right': 0.98, 'top': 0.92, 'bottom': 0.15,
			     'wspace': 0.3, 'hspace': 0.32},
		 	  **kwargs}

	figure = Figure_Lean(ncols = 2, nrows = 1, **kwargs)
	ax = figure.ax

	parameter_list = np.asarray(list(parameters))[np.array([0,2])]

	for counter, parameter in enumerate(parameter_list):

		parameter_dict = parameters[parameter]

		plot_normalized_data(ax[counter], parameter_dict, 
							 parameter_dict['Reference'], parameter_dict['Limit'], 
						     False, parameter, 'darkred', 'Linear normalization')
		plot_normalized_data(ax[counter], parameter_dict, 
							 parameter_dict['Reference'], parameter_dict['Limit'], 
						     True, parameter, 'darkgreen', 'Logarithmic normalization')

	ax[0].text(-0.16, 1.02, 'A', transform=ax[0].transAxes, size = 20, weight='bold')
	ax[1].text(-0.16, 1.02, 'B', transform=ax[1].transAxes, size = 20, weight='bold')

	figure.execute()
	return figure.fig

def main():

	monte_carlo = Monte_Carlo_Analysis('./PV_E/Historical_Data/PV_E_Distance_Time.md')


	plot_normalization(monte_carlo.parameters, 
				       name = 'Normalization_Comparison',
					   directory = './PV_E/Historical_Data/',
					   show = True,
					   save = False)


if __name__ == '__main__':
	main()

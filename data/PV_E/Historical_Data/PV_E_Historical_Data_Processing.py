import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from pyH2A.Utilities.find_nearest import find_nearest
from pyH2A.Utilities.output_utilities import Figure_Lean


def process_PEM_cost_data():
	'''Processes historical PEM cost data from Reichstelstein 2019, conversion from
	2016 EUR/kW to 2016 USD/kW.

	Returns
	-------
	output : ndarray
		Array containing year and cost in 2016 USD/kW for each datapoint.
	average : ndarray
		Array containing one datapoint per year, with the provided cost being the
		average of all datapoints for the given year. 
	'''

	data = pd.read_csv('PEM_Electrolyzer_Cost_Reichelstein_2019.csv', sep = ';', comment = '#')

	output = np.empty((0,2))
	average = []

	for column in data:
		data_clean = data[column].dropna()
		data_np = data_clean.to_numpy()
		data_np *= 1.11  # conversion from 2016 EUR/kW to 2016 USD/kW

		if len(data_np) > 0:
			year_arr = np.ones(len(data_np)) * int(column)
			year_data = np.c_[year_arr, data_np]

			output = np.append(output, year_data, axis = 0)

			average_year_data = [int(column), np.mean(data_np)]

			average.append(average_year_data)

	average = np.vstack(average)

	return output, average

def process_PV_cost_data():
	'''Processes PV module cost data (2019 USD/W) from Lafond (2017)/IRENA (2019), conversion
	to installed PV cost (2019 USD/kW), assuming that module costs makes up 33% of installed PV cost
	(based on PV cost breakdown in IRENA (2019), Renewable Power Generation Costs in 2018, 
	International Renewable Energy Agency, Abu Dhabi.)

	Returns
	-------
	output : ndarray
		Array containing year and cost of installed PV in 2019 USD/kW.
	'''

	data = pd.read_csv('Solar_PV_Module_Prices_1976_2019.csv', sep = ',', comment = '#')
	
	pv_cost_installed = data['Solar PV Module Cost (2019 US$ per W)'].to_numpy() * 1000 * 3 # Conversin of module cost (2019 USD/W) to installed cost (2019 USD/kW)
	years = data['Year'].to_numpy()

	return np.c_[years, pv_cost_installed]

def process_PV_installed_cost_data():
	'''Processes global weighted average total installed solar PV cost, source:
	IRENA (2019), Renewable Power Generation Costs in 2018, International Renewable Energy Agency, Abu Dhabi.

	Returns 
	-------
	output : ndarray
		Array containing year and global weighted average total installed solar PV cost.
	'''

	output = np.genfromtxt('Installed_PV_Cost_IRENA_2019.csv', delimiter = '	')

	return output

class Combined_Data:

	def __init__(self, base_efficiency, limit_efficiency, 
				 yearly_efficiency_increase, pv_base_cost):
		'''
		Parameters
		----------
		base_efficieny : float
			Base efficiency of PEM electrolyzer in kg(H2)/kWh
		limit_efficiency : float
			Maximum possible efficiency of PEM electrolyzer in kg(H2)/kWh
		yearly_efficiency_increase : float
			Yearly increase of efficiency in percentage points.
		pv_base_cost : float
			Installed PV cost in 2020, in USD/kW.
		'''
		self.base_efficiency = base_efficiency
		self.limit_efficiency = limit_efficiency
		self.yearly_efficiency_increase = yearly_efficiency_increase
		self.pv_base_cost = pv_base_cost

		self.pem_cost, self.pem_cost_average = process_PEM_cost_data()
		self.pv_cost = process_PV_cost_data()
		self.pv_global_installed_cost = process_PV_installed_cost_data()

		self.combine_data()

	def calculate_pem_efficiency(self, years):
		'''Calculate PEM efficiency in specificed years.

		Parameters
		----------
		years : ndarray
			Array of years, for which PEM efficiency is to be computed.

		Returns
		-------
		efficiency : ndarray
			Array of PEM efficiencies for specified years in kg(H2)/kWh

		Notes
		-----
		Calculation assumes that the base efficiency is for the year 2020.
		'''

		base_efficiency_fraction = self.base_efficiency/self.limit_efficiency

		years_normalized = years - 2020
		efficiency_fraction = self.yearly_efficiency_increase/100. * years_normalized + base_efficiency_fraction

		efficiency = efficiency_fraction * self.limit_efficiency

		return efficiency

	def combine_data(self):
		'''Combine PV cost, PEM cost and PEM efficiency data.

		Notes
		-----
		PV cost is mapped to PEM cost datapoints. PEM efficiency is calculated
		for years given in PEM cost datapoints.
		'''

		output = self.pem_cost[np.where(self.pem_cost[:,0] <= 2020)[0]]

		pv_cost_array = []

		for entry in output:
			pv_idx = find_nearest(self.pv_cost, entry[0])[0]

			if int(entry[0]) == int(self.pv_cost[pv_idx][0]): # mapping PV cost to PEM cost datapoint years
				pv_cost_array.append(self.pv_cost[pv_idx][1])

			elif int(entry[0]) == 2020:  # setting PV cost to pv_base_cost value for year 2020
				pv_cost_array.append(self.pv_base_cost)

			else:
				raise KeyError(f'{int(entry[0])} not in PV cost data.')

		self.output = np.c_[output, np.asarray(pv_cost_array), self.calculate_pem_efficiency(output[:,0])]

	def save_data(self, file_name, header_string):
		'''Save combined output data.

		Parameters
		----------
		file_name : str
			File name for output file.
		header_string : str
			String for header of file.
		'''

		np.savetxt(Path(file_name), self.output, header = header_string, delimiter = '	')

	def plot_historical_pv_data(self, ax = None, figure_lean = False, **kwargs):

		kwargs = {**{'left': 0.15, 'right': 0.95}, 
				  **kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		ax.plot(self.output[:,0], self.output[:,2], 'o-', color = 'darkgreen',
				label = 'Installed PV cost\n(based on module cost)')
		ax.plot(self.pv_global_installed_cost[:,0], self.pv_global_installed_cost[:,1],
				'o-', color = 'grey', label = 'Installed PV cost\n(IRENA 2019)')

		ax.set_xticks(np.arange(2002, 2021, 4))
		ax.set_xlabel('Year')
		ax.set_ylabel('Installed PV cost / 2019 USD/kW')

		ax.legend()

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		if figure_lean:
			figure.execute()
			return figure.fig

	def plot_historical_PEM_data(self, ax = None, figure_lean = False, **kwargs):
		
		kwargs = {**{'left': 0.15, 'right': 0.95}, 
				  **kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		ax.plot(self.output[:,0], self.output[:,1], '.', color = 'darkblue',
				label = 'PEM electrolyzer cost\n(Reichelstein 2019)', markersize = 10)

		ax.set_xticks(np.arange(2002, 2021, 4))
		ax.set_xlabel('Year')
		ax.set_ylabel('PEM electrolyzer cost / 2016 USD/kW')

		ax.legend()

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		if figure_lean:
			figure.execute()
			return figure.fig

	def plot_historical_efficiency(self, ax = None, figure_lean = False, **kwargs):
		
		kwargs = {**{'left': 0.15, 'right': 0.95}, 
				  **kwargs}

		if ax is None:
			figure = Figure_Lean(**kwargs)
			ax = figure.ax

		ax.plot(self.output[:,0], self.output[:,3], 'o-', color = 'darkblue',
				label = 'PEM electrolyzer efficiency')

		ax.set_xticks(np.arange(2002, 2021, 4))
		ax.set_xlabel('Year')
		ax.set_ylabel(r'PEM electrolyzer efficiency / kg($H_{2}$)/kWh')

		ax.legend()

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

		if figure_lean:
			figure.execute()
			return figure.fig

	def plot_historical_stack_replacement_cost(self, ax):

		ax.plot(self.output[:,0], np.ones(len(self.output)) * 0.4, 'o-',
			color = 'darkblue', label = 'Stack repl. (fr. E-CAPEX)')

		ax.set_xticks(np.arange(2002, 2021, 4))
		ax.set_xlabel('Year')
		ax.set_ylabel('Stack repl. (fr. E-CAPEX)')

		ax.legend()

		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2, zorder = 0)

	def plot_combined(self, **kwargs):

		kwargs = {**{'fig_width': 9, 'fig_height': 7,
					'left': 0.12, 'right': 0.98, 'top': 0.93, 'bottom': 0.08,
					 'wspace': 0.3, 'hspace': 0.32},
				  **kwargs}

		figure = Figure_Lean(ncols = 2, nrows = 2, **kwargs)
		ax = figure.ax

		self.plot_historical_pv_data(ax = ax[0][0])
		self.plot_historical_PEM_data(ax = ax[0][1])
		self.plot_historical_efficiency(ax = ax[1][0])
		self.plot_historical_stack_replacement_cost(ax = ax[1][1])

		ax[0][0].text(-0.07, 1.05, 'A', transform=ax[0][0].transAxes, size = 20, weight='bold')
		ax[0][1].text(-0.07, 1.05, 'B', transform=ax[0][1].transAxes, size = 20, weight='bold')
		ax[1][0].text(-0.07, 1.05, 'C', transform=ax[1][0].transAxes, size = 20, weight='bold')
		ax[1][1].text(-0.07, 1.05, 'D', transform=ax[1][1].transAxes, size = 20, weight='bold')

		figure.execute()
		return figure.fig





def main():
	data = Combined_Data(base_efficiency = 0.0185,
						 limit_efficiency = 0.02538, 
						 yearly_efficiency_increase = 0.4,
						 pv_base_cost = 818)

	# data.save_data('PV_E_Historical_Data.csv', 
	# 			   'Year	\$ / kW(Electrolyzer)	\$ / kW(PV)	kg($H_{2}$) / kWh(Electricity)')



	data.plot_combined(name = 'Combined_Historical_Plots',
					   directory = './',
					   show = True,
					   save = False)

	# pem_cost, pem_cost_average = process_PEM_cost_data()
	# pv_cost = process_PV_cost_data()
	# pv_global_installed_cost = process_PV_installed_cost_data()

	# plt.plot(pv_cost[:,0], pv_cost[:,1])
	# plt.plot(pv_global_installed_cost[:,0], pv_global_installed_cost[:,1])

	# plt.plot(pem_cost[:,0], pem_cost[:,1], '.')
	# plt.plot(pem_cost_average[:,0], pem_cost_average[:,1], 'o-')

	# plt.show()



if __name__ == '__main__':
	main()
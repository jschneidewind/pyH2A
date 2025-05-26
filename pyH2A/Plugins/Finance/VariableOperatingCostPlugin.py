from pyH2A.Utilities.input_modification import insert, sum_all_tables, process_table, read_textfile
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins.Plugin import Plugin
import pyH2A.Utilities.find_nearest as fn
import numpy as np


class VariableOperatingCostPlugin(Plugin):
	'''Calculation of variable operating costs.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Output per Year > Value : float
		Yearly output taking operating capacity factor into account, in (kg of H2)/year.
	Utilities > [...] > Cost : float, ndarray or str
		Cost of utility (e.g. $/kWh for electricity). May be either a float, a ndarray with the
		same length as `dcf.inflation_correction` or a textfile containing cost values (cost values 
		have to be in second column).
	Utilities > [...] > Usage per kg H2 : float
		Usage of utility per kg H2 (e.g. kWh/(kg of H2) for electricity).
	Utilities > [...] > Price Conversion Factor : float
		Conversion factor between cost and usage units. Should be set to 1 if no conversion is
		required.
	Utilities > [...] > Path : str, optional
		Path for `Cost` entry.
	Utilities > [...] > Usage Path : str, optional
		Path for `Usage per kg H2` entry.
	[...] Other Variable Operating Operating Cost [...] >> Value : float
		``sum_all_tables()`` is used.

	Returns
	-------
	[...] Other Variable Operating Cost [...] > Summed Total > Value : float
		Summed total for each individual table in "Other Variable Operating Cost"
		group.
	Variable Operating Costs > Total > Value : ndarray
		Sum of inflation corrected utilities costs and other variable operating costs.
	Variable Operating Costs > Utilities > Value : ndarray
		Sum of inflation corrected utilities costs.
	Variable Operating Costs > Other > Value : float
		Sum of `Other Variable Operating Cost` entries.
	'''

	def __init__(
			self,
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = ['Technical Operating Parameters and Specifications']
		self.process_table(table_keys)
		process_table(self.dcf.inp, 'Utilities', ['Cost', 'Usage per kg H2'], path_key = ['Path', 'Usage Path'])
		self.run_plugin()
		self.process_insert_queue()

	def run_plugin(
			self
			) -> None:
		self.calculate_utilities_cost()
		self.other_variable_costs()

		self.insert_queue.extend([
			{'key': 'Variable Operating Costs', 'subkey': 'Total', 'value': self.utilities + self.other},
			{'key': 'Variable Operating Costs', 'subkey': 'Utilities', 'value': self.utilities},
			{'key': 'Variable Operating Costs', 'subkey': 'Other', 'value': self.other}
		])

	def calculate_utilities_cost(
			self
			) -> None:
		'''Iterating over all utilities and computing summed yearly costs.
		'''
		self.utilities = 0.

		for key in self.dcf.inp['Utilities']:
			utility = Utility(self.dcf.inp['Utilities'][key], self.dcf)
			self.utilities += utility.cost_per_kg_H2

		self.utilities = self.utilities * self.dcf.inp['Technical Operating Parameters and Specifications']['Output per Year']['Value']

	def other_variable_costs(
			self
			) -> None:
		'''Applying ``sum_all_tables()`` to "Other Variable Operating Cost" group.
		'''
		self.other = self.dcf.chemical_inflator * sum_all_tables(self.dcf.inp, 'Other Variable Operating Cost', 'Value', 
																insert_total = True, class_object = self.dcf, 
																print_info = self.dcf.print_info)


class Utility:
	'''Individual utility objects.

	Methods 
	-------
	calculate_cost_per_kg_H2:
		Calculation of utility cost per kg of H2 with inflation correction.
	'''

	def __init__(
			self, 
			dictionary: dict, 
			dcf: DiscountedCashFlow
			) -> None:
		'''Individual utility objects.
		'''
		self.dcf = dcf

		self.calculate_cost_per_kg_H2(dictionary)

	def calculate_cost_per_kg_H2(
			self, 
			dictionary: dict
			) -> None:
		'''Calculation of utility cost per kg of H2 with inflation correction.
		'''
		
		if isinstance(dictionary['Cost'], str):
			prices = read_textfile(dictionary['Cost'], delimiter = '	')
			years_idx = fn.find_nearest(prices, self.dcf.years)
			prices = prices[years_idx]

			self.cost_per_kg_H2 = prices[:,1] * self.dcf.inflation_correction * dictionary['Price Conversion Factor'] * dictionary['Usage per kg H2']

		else:
			annual_cost_per_kg_H2 = self.dcf.inflation_correction * dictionary['Cost'] * dictionary['Usage per kg H2'] * dictionary['Price Conversion Factor']
			self.cost_per_kg_H2 = np.ones(len(self.dcf.inflation_factor)) * annual_cost_per_kg_H2

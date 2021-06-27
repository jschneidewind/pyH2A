from input_modification import insert, sum_all_tables, process_table, read_textfile
import find_nearest as fn
import numpy as np

class Variable_Operating_Cost_Plugin:
	'''
	______________
	Required Input
	______________

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Output per Year | num

	process_table() is used

	# Utilities
	Name | Cost | Usage per kg H2 | Price Conversion Factor | Path | Usage Path (optional)
	--- | --- | --- | ---
	str | num or str | num | num

	process_table() is used for "Cost" column ("Path") and "Usage per kg H2" column ("Usage Path")
	If cost is a str, the provided string is used as a path to access corresponding look-up table with yearly prices. If it is a num, provided value will be used.

	# Other Variable Operating Cost [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	______________
	Output
	______________

	Insertion of "Summed Total" for each sum_all_tables() processed table

	Variable Operating Costs > Total > Value
	Variable Operating Costs > Utilities > Value
	Variable Operating Costs > Other > Value
	'''

	def __init__(variable, self, print_info):
		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')
		#process_table(self.inp, 'Utilities', 'Cost')
		process_table(self.inp, 'Utilities', ['Cost', 'Usage per kg H2'], path_key = ['Path', 'Usage Path'])

		variable.calculate_utilities_cost(self)
		variable.other_variable_costs(self, print_info)

		insert(self, 'Variable Operating Costs', 'Total', 'Value', variable.utilities + variable.other, __name__, print_info = print_info)
		insert(self, 'Variable Operating Costs', 'Utilities', 'Value', variable.utilities, __name__, print_info = print_info)
		insert(self, 'Variable Operating Costs', 'Other', 'Value', variable.other, __name__, print_info = print_info)

	def calculate_utilities_cost(variable, self):

		variable.utilities = 0.

		for key in self.inp['Utilities']:
			utility = Utility(self.inp['Utilities'][key], self)
			variable.utilities += utility.cost_per_kg_H2

		variable.utilities = variable.utilities * self.inp['Technical Operating Parameters and Specifications']['Output per Year']['Value']

	def other_variable_costs(variable, self, print_info):

		variable.other = self.chemical_inflator * sum_all_tables(self.inp, 'Other Variable Operating Cost', 'Value', insert_total = True, class_object = self, print_info = print_info)

class Utility:

	def __init__(util, dictionary, self):
		util.calculate_cost_per_kg_H2(dictionary, self)

	def calculate_cost_per_kg_H2(util, dictionary, self):
		
		if isinstance(dictionary['Cost'], str):
			prices = read_textfile(dictionary['Cost'], delimiter = '	')
			years_idx = fn.find_nearest(prices, self.years)
			prices = prices[years_idx]

			util.cost_per_kg_H2 = prices[:,1] * self.inflation_correction * dictionary['Price Conversion Factor'] * dictionary['Usage per kg H2']

		else:
			annual_cost_per_kg_H2 = self.inflation_correction * dictionary['Cost'] * dictionary['Usage per kg H2'] * dictionary['Price Conversion Factor']
			util.cost_per_kg_H2 = np.ones(len(self.inflation_factor)) * annual_cost_per_kg_H2

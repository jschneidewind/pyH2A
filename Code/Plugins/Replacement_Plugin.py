from input_modification import insert, process_input, sum_all_tables
import numpy as np
import find_nearest as fn

class Replacement_Plugin:
	'''
	______________
	Required Input
	______________

	# Planned Replacement
	Name | Frequency (years) | Cost ($) | Path (optional)
	--- | --- | ---
	str | num | num

	process_input() is used, meaning that if a path is specified, the corresponding value at that path is retrieved and 
	multiplied by "Cost ($)" to obtain the actual replacement cost.

	# Unplanned Replacement [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	______________
	Output
	______________

	Insertion of "Summed Total" for each sum_all_tables() processed table

	Replacement > Total > Value

	'''
	def __init__(replace, self, print_info):
		replace.initialize_yearly_costs(self)
		replace.calculate_planned_replacement(self)
		replace.unplanned_replacement(self, print_info)

		yearly_inflated = replace.yearly * self.inflation_correction * self.inflation_factor

		insert(self, 'Replacement', 'Total', 'Value', yearly_inflated, __name__, print_info = print_info)

	def initialize_yearly_costs(replace, self):

		replace.yearly = np.zeros(len(self.inflation_factor))

	def calculate_planned_replacement(replace, self):

		for key in self.inp['Planned Replacement']:
			planned_replacement = Planned_Replacement(self.inp['Planned Replacement'][key], key, self)
			replace.yearly[planned_replacement.years_idx] += planned_replacement.cost

	def unplanned_replacement(replace, self, print_info):

		replace.unplanned = sum_all_tables(self.inp, 'Unplanned Replacement', 'Value', insert_total = True, class_object = self, print_info = print_info)
		replace.yearly += replace.unplanned

class Planned_Replacement:
	'''Replacement costs are billed annually, replacements which are performed at a non-integer rate are corrected using non_interger_correction
	'''

	def __init__(planned, dictionary, key, self):
		planned.calculate_yearly_cost(dictionary, key, self)
		
	def calculate_yearly_cost(planned, dictionary, key, self):

		replacement_frequency = int(np.ceil(dictionary['Frequency (years)']))
		non_integer_correction = replacement_frequency / dictionary['Frequency (years)']

		raw_replacement_cost = process_input(self.inp, 'Planned Replacement', key, 'Cost ($)')
		initial_replacement_year_idx = fn.find_nearest(self.plant_years, replacement_frequency)[0]

		planned.cost = raw_replacement_cost * non_integer_correction * self.combined_inflator
		planned.years = self.plant_years[initial_replacement_year_idx:][0::replacement_frequency]
		planned.years_idx = fn.find_nearest(self.plant_years, planned.years)
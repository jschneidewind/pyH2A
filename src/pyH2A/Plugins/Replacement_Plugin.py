from pyH2A.Utilities.input_modification import insert, process_input, sum_all_tables
import pyH2A.Utilities.find_nearest as fn
import numpy as np

class Replacement_Plugin:
	'''Calculating yearly overall replacement costs based on one-time replacement costs and frequency.

	Parameters
	----------
	Planned Replacement > [...] > Frequency (years) : float
		Replacement frequency of [...] in years. 
		Iteration over all entries in `Planned Replacement` table.
	Planned Replacement > [...] > Cost ($) : float
		One-time replacement cost of [...].
		Iteration over all entries in `Planned Replacment` table. 
	[...] Unplanned Replacement [...] >> Value : float
		``sum_all_tables()`` is used.

	Returns
	-------
	[...] Unplanned Replacement [...] > Summed Total > Value : float
		Summed total for each individual table in "Unplanned Replacement" group.
	Replacement > Total > Value : ndarray
		Total inflated replacement costs (sum of `Planned Replacement` entries and
		unplanned replacement costs).
	'''
	def __init__(self, dcf, print_info):
		self.initialize_yearly_costs(dcf)
		self.calculate_planned_replacement(dcf)
		self.unplanned_replacement(dcf, print_info)

		yearly_inflated = self.yearly * dcf.inflation_correction * dcf.inflation_factor


		insert(dcf, 'Replacement', 'Total', 'Value', yearly_inflated, __name__, print_info = print_info)

	def initialize_yearly_costs(self, dcf):
		'''Initializes ndarray filled with zeros with same length as dcf.inflation_factor.
		'''

		self.yearly = np.zeros(len(dcf.inflation_factor))

	def calculate_planned_replacement(self, dcf):
		'''Calculation of yearly replacement costs by iterating over all entries of 
		`Planned Replacement`.
		'''

		for key in dcf.inp['Planned Replacement']:
			planned_replacement = Planned_Replacement(dcf.inp['Planned Replacement'][key], key, dcf)
			self.yearly[planned_replacement.years_idx] += planned_replacement.cost

	def unplanned_replacement(self, dcf, print_info):
		'''Calculating unplanned replacement costs by appling ``sum_all_tables()`` to 
		"Unplanned Replacement" group.
		'''

		self.unplanned = sum_all_tables(dcf.inp, 'Unplanned Replacement', 'Value', 
										insert_total = True, class_object = dcf, 
										print_info = print_info)
		self.yearly += self.unplanned

class Planned_Replacement:
	'''
	Individual planned replacement objects.

	Methods
	-------
	calculate_yearly_cost:
		Calculation of yearly costs from one-time cost and replacement frequency.
	'''

	def __init__(self, dictionary, key, dcf):
		self.calculate_yearly_cost(dictionary, key, dcf)
		
	def calculate_yearly_cost(self, dictionary, key, dcf):
		'''Calculation of yearly replacement costs.

		Replacement costs are billed annually, replacements which are performed at a non-integer rate 
		are corrected using non_integer_correction.
		'''

		replacement_frequency = int(np.ceil(dictionary['Frequency (years)']))
		non_integer_correction = replacement_frequency / dictionary['Frequency (years)']

		raw_replacement_cost = process_input(dcf.inp, 'Planned Replacement', key, 'Cost ($)')
		initial_replacement_year_idx = fn.find_nearest(dcf.plant_years, replacement_frequency)[0]

		self.cost = raw_replacement_cost * non_integer_correction * dcf.combined_inflator
		self.years = dcf.plant_years[initial_replacement_year_idx:][0::replacement_frequency]
		self.years_idx = fn.find_nearest(dcf.plant_years, self.years)
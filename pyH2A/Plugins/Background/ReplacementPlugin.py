from pyH2A.Utilities.input_modification import sum_all_tables, process_input
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
import pyH2A.Utilities.find_nearest as fn
import numpy as np

class ReplacementPlugin(Plugin):
	'''Calculating yearly overall replacement costs based on one-time replacement costs and frequency.

	Parameters
	----------
	Planned Replacement > [...] > Frequency (years) : float
		Replacement frequency of [...] in years. 
		Iteration over all entries in `Planned Replacement` table. No path key
		available.
	Planned Replacement > [...] > Cost ($) : float
		One-time replacement cost of [...].
		Iteration over all entries in `Planned Replacement` table. Path key
		is 'Path'.
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
	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		# process_table(dcf.inp, 'Planned Replacement', ['Cost ($)', 'Frequency (years)'], 
		# 				path_key = ['Path', 'Frequency Path'])

		super().__init__(dcf)

		self.initialize_yearly_costs()
		self.initialize_contributions()
		self.calculate_planned_replacement()
		self.unplanned_replacement()

		self.contributions['Total'] = np.sum(self.yearly)
		
		yearly_inflated = self.yearly * self.dcf.inflation_correction * self.dcf.inflation_factor

		self.insert_queue.append(
			{'key': 'Replacement', 'subkey': 'Total', 'value': yearly_inflated}
		)
		self.process_insert_queue()

	def initialize_yearly_costs(
			self
			) -> None:
		'''Initializes ndarray filled with zeros with same length as dcf.inflation_factor.
		'''

		self.yearly = np.zeros(len(self.dcf.inflation_factor))

	def initialize_contributions(
			self
			) -> None:
		'''Initializes contributions to replacement costs.
		'''
		self.contributions = {}
		self.contributions['Data'] = {}
		self.contributions['Table Group'] = 'Replacement Costs'

	def calculate_planned_replacement(
			self
			) -> None:
		'''Calculation of yearly replacement costs by iterating over all entries of 
		`Planned Replacement`.
		'''

		for key in self.dcf.inp['Planned Replacement']:
			planned_replacement = PlannedReplacement(self.dcf.inp['Planned Replacement'][key], key, self.dcf)
			self.yearly[planned_replacement.years_idx] += planned_replacement.cost
			self.contributions['Data'][key] = planned_replacement.total_cost

	def unplanned_replacement(
			self
			) -> None:
		'''Calculating unplanned replacement costs by appling ``sum_all_tables()`` to 
		"Unplanned Replacement" group.
		'''

		self.unplanned = sum_all_tables(self.dcf.inp, 'Unplanned Replacement', 'Value', 
										insert_total = True, class_object = self.dcf, 
										print_info = self.dcf.print_info)
		self.yearly += self.unplanned
		self.contributions['Data']['Unplanned Replacement'] = np.sum(np.ones_like(self.yearly) * self.unplanned)

class PlannedReplacement:
	'''
	Individual planned replacement objects.

	Methods
	-------
	calculate_yearly_cost:
		Calculation of yearly costs from one-time cost and replacement frequency.
	'''

	def __init__(
			self, 
			dictionary: dict, 
			key: str, 
			dcf: DiscountedCashFlow
			) -> None:
		self.dcf = dcf 

		self.calculate_yearly_cost(dictionary, key)
		
	def calculate_yearly_cost(
			self, 
			dictionary: dict, 
			key: str
			) -> None:
		'''Calculation of yearly replacement costs.

		Replacement costs are billed annually, replacements which are performed at a non-integer rate 
		are corrected using non_integer_correction.
		'''
		replacement_frequency = int(np.ceil(dictionary['Frequency (years)']))
		non_integer_correction = replacement_frequency / dictionary['Frequency (years)']

		raw_replacement_cost = process_input(self.dcf.inp, 'Planned Replacement', key, 'Cost ($)')
		initial_replacement_year_idx = fn.find_nearest(self.dcf.plant_years, replacement_frequency)[0]

		self.cost = raw_replacement_cost * non_integer_correction * self.dcf.combined_inflator
		self.years = self.dcf.plant_years[initial_replacement_year_idx:][0::replacement_frequency]
		self.years_idx = fn.find_nearest(self.dcf.plant_years, self.years)

		self.total_cost = np.sum(np.ones_like(self.years) * self.cost)
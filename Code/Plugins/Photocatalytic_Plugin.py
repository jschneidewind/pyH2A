import numpy as np
from Energy_Conversion import Energy, kWh, eV
from input_modification import insert, process_table

class Photocatalytic_Plugin:
	'''
	______________
	Required Input
	______________

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Design Output per Day | num

	process_table() is used

	# Reactor Baggies
	Name | Value
	--- | ---
	Cost Material Top ($/m2) | num
	Cost Material Bottom ($/m2) | num
	Number of ports | num
	Cost of port ($) | num
	Other Costs ($) | num
	Markup factor | num
	Length (m) | num
	Width (m) | num
	Height (m) | num
	Additional land area (%) | num
	Lifetime (years) | num

	process_table() is used

	# Catalyst
	Name | Value
	--- | ---
	Cost per kg ($) | num
	Concentration (kg/L) | num
	Lifetime (years) | num

	process_table() is used

	# Solar-to-Hydrogen Efficiency
	Name | Value
	--- | ---
	STH (%) | num

	process_table() is used

	# Solar Input
	Name | Value
	--- | ---
	Mean solar input (kWh/m2/day) | num

	process_table() is used

	______________
	Output
	______________

	Non-Depreciable Capital Costs > Land required (acres) > Value
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value
	Planned Replacement > Planned Replacement Catalyst > Cost ($)
	Planned Replacement > Planned Replacement Catalyst > Frequency (years)
	Planned Replacement > Planned Replacement Baggie > Cost ($)
	Planned Replacement > Planned Replacement Baggie > Frequency (years)
	Direct Capital Costs > Baggie Cost ($) > Value
	Direct Capital Costs > Catalyst Cost ($) > Value
	Reactor Baggies > Number > Value
	'''

	def __init__(photo, self, print_info):
		process_table(self.inp, 'Reactor Baggies', 'Value')
		process_table(self.inp, 'Solar Input', 'Value')
		process_table(self.inp, 'Solar-to-Hydrogen Efficiency', 'Value')

		photo.hydrogen_production(self)

		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')

		photo.baggie_cost(self)

		process_table(self.inp, 'Catalyst', 'Value')

		photo.catalyst_cost(self)
		photo.land_area(self)

		insert(self, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', photo.total_land_area_acres, __name__, print_info = print_info)
		insert(self, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', photo.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(self, 'Planned Replacement', 'Planned Replacement Catalyst', 'Cost ($)', photo.catalyst_cost, __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Catalyst', 'Frequency (years)', self.inp['Catalyst']['Lifetime (years)']['Value'], __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Baggie', 'Cost ($)', photo.baggies_cost, __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Baggie', 'Frequency (years)', self.inp['Reactor Baggies']['Lifetime (years)']['Value'], __name__, print_info = print_info)

		insert(self, 'Direct Capital Costs', 'Baggie Cost ($)', 'Value', photo.baggies_cost, __name__, print_info = print_info)
		insert(self, 'Direct Capital Costs', 'Catalyst Cost ($)', 'Value', photo.catalyst_cost, __name__, print_info = print_info)

		insert(self, 'Reactor Baggies', 'Number', 'Value', photo.baggie_number, __name__, print_info = print_info)

	def hydrogen_production(photo, self):

		baggie = self.inp['Reactor Baggies']

		photo.baggie_area = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value']
		baggie_insolation = Energy(photo.baggie_area * self.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_baggie = (baggie_insolation.J * self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		photo.kg_H2_per_baggie = (2 * mol_H2_per_baggie)/1000.

	def baggie_cost(photo, self):

		baggie = self.inp['Reactor Baggies']

		material_cost = photo.baggie_area * (baggie['Cost Material Top ($/m2)']['Value'] + baggie['Cost Material Bottom ($/m2)']['Value'])
		port_cost = baggie['Number of ports']['Value'] * baggie['Cost of port ($)']['Value']

		cost_per_baggie = baggie['Markup factor']['Value'] * (material_cost + port_cost + baggie['Other Costs ($)']['Value'])

		photo.baggie_number = np.ceil(self.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / photo.kg_H2_per_baggie)
		photo.baggies_cost = photo.baggie_number * cost_per_baggie

	def catalyst_cost(photo, self):

		baggie = self.inp['Reactor Baggies']

		baggie_volume = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value'] * baggie['Height (m)']['Value']
		catalyst_amount_per_baggie = baggie_volume * self.inp['Catalyst']['Concentration (kg/L)']['Value']
		catalyst_amount = catalyst_amount_per_baggie * photo.baggie_number

		photo.catalyst_cost = catalyst_amount * self.inp['Catalyst']['Cost per kg ($)']['Value']

	def land_area(photo, self):

		baggie_land_area = photo.baggie_number * photo.baggie_area
		total_land_area = baggie_land_area * (1. + self.inp['Reactor Baggies']['Additional land area (%)']['Value'])

		photo.total_land_area_acres = total_land_area * 0.000247105
		photo.total_solar_collection_area = baggie_land_area

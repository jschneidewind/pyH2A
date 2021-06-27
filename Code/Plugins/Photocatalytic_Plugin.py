import numpy as np
from Energy_Conversion import Energy, kWh, eV
from input_modification import insert, process_table
import matplotlib.pyplot as plt
from timeit import default_timer as timer

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
	Direct Capital Costs - Reactor Baggies > Baggie Cost ($) > Value
	Direct Capital Costs - Photocatalyst > Catalyst Cost ($) > Value
	Reactor Baggies > Number > Value
	Catalyst > Properties > Value

	______________
	Other Output
	______________

	['Photocatalytic_Plugin'].catalyst_properties attribute

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

		photo.catalyst_activity(self)

		insert(self, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', photo.total_land_area_acres, __name__, print_info = print_info)
		insert(self, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', photo.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(self, 'Planned Replacement', 'Planned Replacement Catalyst', 'Cost ($)', photo.catalyst_cost, __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Catalyst', 'Frequency (years)', self.inp['Catalyst']['Lifetime (years)']['Value'], __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Baggie', 'Cost ($)', photo.baggies_cost, __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement Baggie', 'Frequency (years)', self.inp['Reactor Baggies']['Lifetime (years)']['Value'], __name__, print_info = print_info)

		insert(self, 'Direct Capital Costs - Reactor Baggies', 'Baggie Cost ($)', 'Value', photo.baggies_cost, __name__, print_info = print_info)
		insert(self, 'Direct Capital Costs - Photocatalyst', 'Catalyst Cost ($)', 'Value', photo.catalyst_cost, __name__, print_info = print_info)

		insert(self, 'Reactor Baggies', 'Number', 'Value', photo.baggie_number, __name__, print_info = print_info)
		insert(self, 'Catalyst', 'Properties', 'Value', photo.catalyst_properties, __name__, print_info = print_info)

	def hydrogen_production(photo, self):

		baggie = self.inp['Reactor Baggies']

		photo.baggie_area = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value']
		baggie_insolation = Energy(photo.baggie_area * self.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_baggie = (baggie_insolation.J * 
					self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol

		photo.kg_H2_per_baggie = (2 * mol_H2_per_baggie)/1000.

	def catalyst_activity(photo, self):

		catalyst_properties = {}

		peak_hourly_irradiation_per_m2 = np.amax(self.inp['Solar Input']['Hourly (kWh/m2)']['Value'])
		peak_hourly_irradiation_per_m2 = Energy(peak_hourly_irradiation_per_m2, kWh)

		peak_mol_H2_per_m2_per_h = (peak_hourly_irradiation_per_m2.J * 
								self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2 * 1.229, eV).Jmol

		mean_daily_mol_H2_per_m2 = (Energy(self.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh).J *
									self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2 * 1.229, eV).Jmol

		kg_catalyst_per_m2 = ((self.inp['Reactor Baggies']['Height (m)']['Value'] * 1000) * 
								self.inp['Catalyst']['Concentration (kg/L)']['Value'])

		activity_mmol_H2_per_h_per_g_catalyst = 1000 * peak_mol_H2_per_m2_per_h / (kg_catalyst_per_m2 * 1000)

		catalyst_properties['Peak activity / mmol H2/h/g'] = activity_mmol_H2_per_h_per_g_catalyst
		catalyst_properties['Peak H2 production / mol H2/m2/h'] = peak_mol_H2_per_m2_per_h
		catalyst_properties['Catalyst Conc. / kg/m2'] = kg_catalyst_per_m2
		catalyst_properties['Catalyst Conc. / kg/L'] = self.inp['Catalyst']['Concentration (kg/L)']['Value']
	
		if 'Molar Weight (g/mol)' in self.inp['Catalyst']:

			catalyst_mol_per_L = ((self.inp['Catalyst']['Concentration (kg/L)']['Value'] * 1000) /
								   self.inp['Catalyst']['Molar Weight (g/mol)']['Value'])

			liter_per_m2 = self.inp['Reactor Baggies']['Height (m)']['Value'] * 1000

			mol_catalyst_per_m2 = liter_per_m2 * catalyst_mol_per_L

			peak_TOF_hourly = peak_mol_H2_per_m2_per_h / mol_catalyst_per_m2
			average_TOF_daily = mean_daily_mol_H2_per_m2 / mol_catalyst_per_m2
			TON = average_TOF_daily * self.inp['Catalyst']['Lifetime (years)']['Value'] * 365

			catalyst_properties['Homogeneous'] = {}
			catalyst_properties['Homogeneous']['Catalyst Conc. / mol/L'] = catalyst_mol_per_L
			catalyst_properties['Homogeneous']['Catalyst Conc. / mol/m2'] = mol_catalyst_per_m2
			catalyst_properties['Homogeneous']['Peak TOF / h^-1'] = peak_TOF_hourly
			catalyst_properties['Homogeneous']['Mean daily TOF / d^-1'] = average_TOF_daily
			catalyst_properties['Homogeneous']['TON'] = TON

			if 'Molar Attenuation Coefficient (M^-1 cm^-1)' in self.inp['Catalyst']:
				absorbance = (catalyst_mol_per_L * (self.inp['Reactor Baggies']['Height (m)']['Value'] * 100) * 
						self.inp['Catalyst']['Molar Attenuation Coefficient (M^-1 cm^-1)']['Value'])

				catalyst_properties['Homogeneous']['Absorbance'] = absorbance
				catalyst_properties['Homogeneous']['Absorbed light (%)'] = 100 * (1 - 10**(-absorbance))

			kg_H2_per_day_TOF_calculation = 1000 * photo.catalyst_amount / self.inp['Catalyst']['Molar Weight (g/mol)']['Value'] * average_TOF_daily * 2. / 1000.
			kg_H2_per_day_baggie_calculation = photo.kg_H2_per_baggie * photo.baggie_number

			assert abs(kg_H2_per_day_TOF_calculation - kg_H2_per_day_baggie_calculation) < 1e-6, 'Difference between baggie and TOF calculation for daily H2 production: TOF: {0}, Baggie: {0}.'.format(
					kg_H2_per_day_TOF_calculation, kg_H2_per_day_baggie_calculation)

		photo.catalyst_properties = catalyst_properties

	def baggie_cost(photo, self):

		baggie = self.inp['Reactor Baggies']

		material_cost = photo.baggie_area * (baggie['Cost Material Top ($/m2)']['Value'] + baggie['Cost Material Bottom ($/m2)']['Value'])
		port_cost = baggie['Number of ports']['Value'] * baggie['Cost of port ($)']['Value']

		cost_per_baggie = baggie['Markup factor']['Value'] * (material_cost + port_cost + baggie['Other Costs ($)']['Value'])

		photo.baggie_number = np.ceil(self.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / photo.kg_H2_per_baggie)
		photo.baggies_cost = photo.baggie_number * cost_per_baggie

	def catalyst_cost(photo, self):

		baggie = self.inp['Reactor Baggies']

		baggie_volume_m3 = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value'] * baggie['Height (m)']['Value']
		baggie_volume_liters = baggie_volume_m3 * 1000

		photo.catalyst_amount_per_baggie = baggie_volume_liters * self.inp['Catalyst']['Concentration (kg/L)']['Value']
		photo.catalyst_amount = photo.catalyst_amount_per_baggie * photo.baggie_number

		photo.catalyst_cost = photo.catalyst_amount * self.inp['Catalyst']['Cost per kg ($)']['Value']

	def land_area(photo, self):

		baggie_land_area = photo.baggie_number * photo.baggie_area
		total_land_area = baggie_land_area * (1. + self.inp['Reactor Baggies']['Additional land area (%)']['Value'])

		photo.total_land_area_acres = total_land_area * 0.000247105
		photo.total_solar_collection_area = baggie_land_area

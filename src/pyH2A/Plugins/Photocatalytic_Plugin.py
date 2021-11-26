import numpy as np
from pyH2A.Utilities.Energy_Conversion import Energy, kWh, eV
from pyH2A.Utilities.input_modification import insert, process_table

class Photocatalytic_Plugin:
	'''Simulating H2 production using photocatalytic water splitting in plastic baggie reactors.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output in (kg of H2)/day, ``process_table()`` is used.
	Reactor Baggies > Cost Material Top ($/m2) > Value : float
		Cost of baggie top material in $/m2.
	Reactor Baggies > Cost Material Bottom ($/m2) > Value : float
		Cost of baggie bottom material in $/m2.
	Reactor Baggies > Number of ports > Value : int
		Number of ports per baggie.
	Reactor Baggies > Other Costs ($) > Value : float
		Other costs per baggie.
	Reactor Baggies > Markup factor > Value : float
		Markup factor for baggies, typically > 1.
	Reactor Baggies > Length (m) > Value : float
		Length of single baggie in m.
	Reactor Baggies > Width (m) > Value : float
		Width of single baggie in m.
	Reactor Baggies > Height (m) > Value : float
		Height of reactor baggie in m. In this simulation this value determines the height
		of the water level and hence is an important parameter ultimately determining the
		level of light absorption and total catalyst amount.
	Reactor Baggies > Additional land area (%) > Value : float
		Additional land area required, percentage or value > 0. 
		Calculated as: (1 + addtional land area) * baggie area.
	Reactor Baggies > Lifetime (years) > Value : float
		Lifetime of reactor baggies in years before replacement is required.
	Catalyst > Cost per kg ($) > Value : float
		Cost per kg of catalyst.
	Catalyst > Concentration (g/L) > Value : float
		Concentration of catalyst in g/L.
	Catalyst > Lifetime (years) > Value : float
		Lifetime of catalysts in year before replacement is required.
	Catalyst > Molar Weight (g/mol) > Value : float, optional
		If the molar weight of the catalyst (in g/mol) is specified, homogeneous catalyst
		properties (TON, TOF etc. are calculated).
	Catalyst > Molar Attenuation Coefficient (M^-1 cm^-1) > Value : float, optional
		If the molar attenuation coefficient (in M^-1 cm^-1) is specified (along with the molar weight),
		absorbance and the fraction of absorbed light are also calculated.
	Solar-to-Hydrogen Efficiency > STH (%) > Value : float
		Solar-to-hydrogen efficiency in percentage or as a value between 0 and 1.
	Solar Input > Mean solar input (kWh/m2/day) > Value : float
		Mean solar input in kWh/m2/day, ``process_table()`` is used.

	Returns
	-------
	Non-Depreciable Capital Costs > Land required (acres) > Value : float
		Total land area required in acres.
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
		Solar colelction area in m2.
	Planned Replacement > Planned Replacement Catalyst > Cost ($) : float
		Total cost of completely replacing the catalyst once.
	Planned Replacement > Planned Replacement Catalyst > Frequency (years) : float
		Replacement frequency of catalyst in years, identical to catalyst lifetime.
	Planned Replacement > Planned Replacement Baggie > Cost ($) : float
		Total cost of replacing all  baggies.
	Planned Replacement > Planned Replacement Baggie > Frequency (years) : float
		Replacement frequency of baggies in year, identical to baggie lifetime.
	Direct Capital Costs - Reactor Baggies > Baggie Cost ($) > Value : float
		Total baggie cost.
	Direct Capital Costs - Photocatalyst > Catalyst Cost ($) > Value : float
		Total catalyst cost.
	Reactor Baggies > Number > Value : int
		Number of individual baggies required for design H2 production capacity.
	Catalyst > Properties > Value : dict
		Dictionary containing detailed catalyst properties calculated from provided parameters.
	['Photocatalytic_Plugin'].catalyst_properties : dict
		Attribute containing catalyst properties dictionary.
	'''

	def __init__(self, dcf, print_info):
		process_table(dcf.inp, 'Reactor Baggies', 'Value')
		process_table(dcf.inp, 'Solar Input', 'Value')
		process_table(dcf.inp, 'Solar-to-Hydrogen Efficiency', 'Value')

		self.hydrogen_production(dcf)

		process_table(dcf.inp, 'Technical Operating Parameters and Specifications', 'Value')

		self.baggie_cost(dcf)

		process_table(dcf.inp, 'Catalyst', 'Value')

		self.catalyst_cost(dcf)
		self.land_area(dcf)

		self.catalyst_activity(dcf)

		insert(dcf, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', 
				self.total_land_area_acres, __name__, print_info = print_info)
		insert(dcf, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', 
				self.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(dcf, 'Planned Replacement', 'Planned Replacement Catalyst', 'Cost ($)', 
				self.catalyst_cost, __name__, print_info = print_info)
		insert(dcf, 'Planned Replacement', 'Planned Replacement Catalyst', 'Frequency (years)', 
				dcf.inp['Catalyst']['Lifetime (years)']['Value'], __name__, print_info = print_info)
		insert(dcf, 'Planned Replacement', 'Planned Replacement Baggie', 'Cost ($)', 
				self.baggies_cost, __name__, print_info = print_info)
		insert(dcf, 'Planned Replacement', 'Planned Replacement Baggie', 'Frequency (years)', 
				dcf.inp['Reactor Baggies']['Lifetime (years)']['Value'], __name__, print_info = print_info)

		insert(dcf, 'Direct Capital Costs - Reactor Baggies', 'Baggie Cost ($)', 'Value', 
				self.baggies_cost, __name__, print_info = print_info)
		insert(dcf, 'Direct Capital Costs - Photocatalyst', 'Catalyst Cost ($)', 'Value', 
				self.catalyst_cost, __name__, print_info = print_info)

		insert(dcf, 'Reactor Baggies', 'Number', 'Value', self.baggie_number, __name__, print_info = print_info)
		insert(dcf, 'Catalyst', 'Properties', 'Value', self.catalyst_properties, __name__, print_info = print_info)

	def hydrogen_production(self, dcf):
		'''Calculation of hydrogen produced per day per baggie (in kg).
		'''

		baggie = dcf.inp['Reactor Baggies']

		self.baggie_area = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value']
		baggie_insolation = Energy(self.baggie_area * dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_baggie = (baggie_insolation.J * 
					dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol

		self.kg_H2_per_baggie = (2 * mol_H2_per_baggie)/1000.

	def catalyst_activity(self, dcf):
		'''Calculation of detailed catalyst properties based on provided parameters. If "Molar Weight (g/mol)"
		is specified in "Catalyst" table properties of a homogeneous catalyst are also calculated. Furthermore,
		if "Molar Attenuation Coefficient (M^-1 cm^-1)" is also provided, the light absorption properties 
		are calculated.
		'''

		catalyst_properties = {}

		peak_hourly_irradiation_per_m2 = np.amax(dcf.inp['Solar Input']['Hourly (kWh/m2)']['Value'])
		peak_hourly_irradiation_per_m2 = Energy(peak_hourly_irradiation_per_m2, kWh)

		peak_mol_H2_per_m2_per_h = (peak_hourly_irradiation_per_m2.J * 
								dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2 * 1.229, eV).Jmol

		mean_daily_mol_H2_per_m2 = (Energy(dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh).J *
									dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2 * 1.229, eV).Jmol

		kg_catalyst_per_m2 = ((dcf.inp['Reactor Baggies']['Height (m)']['Value'] * 1000) * 
								dcf.inp['Catalyst']['Concentration (g/L)']['Value']/1000.)

		activity_mmol_H2_per_h_per_g_catalyst = 1000 * peak_mol_H2_per_m2_per_h / (kg_catalyst_per_m2 * 1000)

		catalyst_properties['Peak activity / mmol H2/h/g'] = activity_mmol_H2_per_h_per_g_catalyst
		catalyst_properties['Peak H2 production / mol H2/m2/h'] = peak_mol_H2_per_m2_per_h
		catalyst_properties['Catalyst Conc. / kg/m2'] = kg_catalyst_per_m2
		catalyst_properties['Catalyst Conc. / g/L'] = dcf.inp['Catalyst']['Concentration (g/L)']['Value']
	
		if 'Molar Weight (g/mol)' in dcf.inp['Catalyst']:

			catalyst_mol_per_L = ((dcf.inp['Catalyst']['Concentration (g/L)']['Value']) /
								   dcf.inp['Catalyst']['Molar Weight (g/mol)']['Value'])

			liter_per_m2 = dcf.inp['Reactor Baggies']['Height (m)']['Value'] * 1000

			mol_catalyst_per_m2 = liter_per_m2 * catalyst_mol_per_L

			peak_TOF_hourly = peak_mol_H2_per_m2_per_h / mol_catalyst_per_m2
			average_TOF_daily = mean_daily_mol_H2_per_m2 / mol_catalyst_per_m2
			TON = average_TOF_daily * dcf.inp['Catalyst']['Lifetime (years)']['Value'] * 365

			catalyst_properties['Homogeneous'] = {}
			catalyst_properties['Homogeneous']['Catalyst Conc. / mol/L'] = catalyst_mol_per_L
			catalyst_properties['Homogeneous']['Catalyst Conc. / mol/m2'] = mol_catalyst_per_m2
			catalyst_properties['Homogeneous']['Peak TOF / h^-1'] = peak_TOF_hourly
			catalyst_properties['Homogeneous']['Mean daily TOF / d^-1'] = average_TOF_daily
			catalyst_properties['Homogeneous']['TON'] = TON

			if 'Molar Attenuation Coefficient (M^-1 cm^-1)' in dcf.inp['Catalyst']:
				absorbance = (catalyst_mol_per_L * (dcf.inp['Reactor Baggies']['Height (m)']['Value'] * 100) * 
						dcf.inp['Catalyst']['Molar Attenuation Coefficient (M^-1 cm^-1)']['Value'])

				catalyst_properties['Homogeneous']['Absorbance'] = absorbance
				catalyst_properties['Homogeneous']['Absorbed light (%)'] = 100 * (1 - 10**(-absorbance))

			kg_H2_per_day_TOF_calculation = 1000 * self.catalyst_amount / dcf.inp['Catalyst']['Molar Weight (g/mol)']['Value'] * average_TOF_daily * 2. / 1000.
			kg_H2_per_day_baggie_calculation = self.kg_H2_per_baggie * self.baggie_number

			assert abs(kg_H2_per_day_TOF_calculation - kg_H2_per_day_baggie_calculation) < 1e-6, 'Difference between baggie and TOF calculation for daily H2 production: TOF: {0}, Baggie: {0}.'.format(
					kg_H2_per_day_TOF_calculation, kg_H2_per_day_baggie_calculation)

		self.catalyst_properties = catalyst_properties

	def baggie_cost(self, dcf):
		'''Calculation of cost per baggie, number of required baggies and total baggie cost.
		'''

		baggie = dcf.inp['Reactor Baggies']

		material_cost = self.baggie_area * (baggie['Cost Material Top ($/m2)']['Value'] + baggie['Cost Material Bottom ($/m2)']['Value'])
		port_cost = baggie['Number of ports']['Value'] * baggie['Cost of port ($)']['Value']

		cost_per_baggie = baggie['Markup factor']['Value'] * (material_cost + port_cost + baggie['Other Costs ($)']['Value'])

		self.baggie_number = np.ceil(dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / self.kg_H2_per_baggie)
		self.baggies_cost = self.baggie_number * cost_per_baggie

	def catalyst_cost(self, dcf):
		'''Calculation of individual baggie volume, catalyst amount per baggie, total catalyst amount 
		and total catalyst cost.
		'''

		baggie = dcf.inp['Reactor Baggies']

		baggie_volume_m3 = baggie['Length (m)']['Value'] * baggie['Width (m)']['Value'] * baggie['Height (m)']['Value']
		baggie_volume_liters = baggie_volume_m3 * 1000

		self.catalyst_amount_per_baggie = baggie_volume_liters * dcf.inp['Catalyst']['Concentration (g/L)']['Value']/1000.
		self.catalyst_amount = self.catalyst_amount_per_baggie * self.baggie_number

		self.catalyst_cost = self.catalyst_amount * dcf.inp['Catalyst']['Cost per kg ($)']['Value']

	def land_area(self, dcf):
		'''Calculation of total required land area and solar collection area.
		'''

		baggie_land_area = self.baggie_number * self.baggie_area
		total_land_area = baggie_land_area * (1. + dcf.inp['Reactor Baggies']['Additional land area (%)']['Value'])

		self.total_land_area_acres = total_land_area * 0.000247105
		self.total_solar_collection_area = baggie_land_area

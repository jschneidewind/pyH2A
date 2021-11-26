from pyH2A.Utilities.Energy_Conversion import Energy, kWh, eV
from pyH2A.Utilities.input_modification import insert, process_table

class Solar_Thermal_Plugin:
	'''Simulation of hydrogen production using solar thermal water splitting.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output of hydrogen production plant per day in kg.
	Solar-to-Hydrogen Efficiency > STH (%) > Value : float
		Solar-to-Hydrogen Efficiency of thermal water splitting process. Percentage of value 
		between 0 and 1.
	Solar Input > Mean solar input (kWh/m2/day) > Value : float
		Mean solar input in kWh/m2/day.
	Non-Depreciable Capital Costs > Additional Land Area (%) > Value : float
		Additional land area required. Percentage or value > 0. Calculated as:
		(1 + Addtional Land Area) * solar collection area.

	Returns
	-------
	Non-Depreciable Capital Costs > Land required (acres) > Value : float
		Total land requirement in acres.
	'''
	
	def __init__(therm, dcf, print_info):
		process_table(dcf.inp, 'Technical Operating Parameters and Specifications', 'Value')
		process_table(dcf.inp, 'Solar-to-Hydrogen Efficiency', 'Value')
		process_table(dcf.inp, 'Solar Input', 'Value')
		process_table(dcf.inp, 'Non-Depreciable Capital Costs', 'Value')

		therm.calculate_land_area(dcf)

		insert(dcf, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', therm.area_acres, __name__, print_info = print_info)

	def calculate_land_area(therm, dcf):
		'''Calculation of required land area based on solar input, solar-to-hydrogen efficiency
		and addtional land are requirements.
		'''

		insolation_per_m2_per_day = Energy(dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_m2_per_day = (insolation_per_m2_per_day.J * dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		kg_H2_per_m2_per_day = (2 * mol_H2_per_m2_per_day)/1000.

		required_area_m2 = dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / kg_H2_per_m2_per_day

		therm.area_m2 = required_area_m2 * (1. + dcf.inp['Non-Depreciable Capital Costs']['Additional Land Area (%)']['Value'])
		therm.area_acres = therm.area_m2 * 0.000247105

from Energy_Conversion import Energy, kWh, eV
from input_modification import insert, process_table

class Solar_Thermal_Plugin:
	'''
	______________
	Required Input
	______________

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Design Output per Day | num

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

	# Non-Depreciable Capital Costs
	Name | Value
	--- | ---
	Additional Land Area (%) | num

	process_table() is used

	______________
	Output
	______________

	Non-Depreciable Capital Costs > Land required (acres) > Value	
	'''


	def __init__(therm, self, print_info):
		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')
		process_table(self.inp, 'Solar-to-Hydrogen Efficiency', 'Value')
		process_table(self.inp, 'Solar Input', 'Value')
		process_table(self.inp, 'Non-Depreciable Capital Costs', 'Value')

		therm.calculate_land_area(self)

		insert(self, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', therm.area_acres, __name__, print_info = print_info)

	def calculate_land_area(therm, self):

		insolation_per_m2_per_day = Energy(self.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_m2_per_day = (insolation_per_m2_per_day.J * self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		kg_H2_per_m2_per_day = (2 * mol_H2_per_m2_per_day)/1000.

		required_area_m2 = self.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / kg_H2_per_m2_per_day

		therm.area_m2 = required_area_m2 * (1. + self.inp['Non-Depreciable Capital Costs']['Additional Land Area (%)']['Value'])
		therm.area_acres = therm.area_m2 * 0.000247105

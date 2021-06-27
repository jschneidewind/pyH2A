import numpy as np
from Energy_Conversion import Energy, kWh, eV
from input_modification import insert, process_table

class PEC_Plugin:
	'''
	______________
	Required Input
	______________

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Design Output per Day | num

	process_table() is used

	# PEC Cells
	Name | Value
	--- | ---
	Cell Cost ($/m2)| num
	Lifetime (years) | num
	Length (m) | num
	Width (m) | num

	process_table() is used

	# Land Area Requirement
	Name | Value
	--- | ---
	Cell Angle (degree) | num
	South Spacing (m) | num
	East/West Spacing (m) | num

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
	Optional Input
	______________

	# Solar Concentrator
	Name | Value
	--- | ---
	Concentration Factor | num

	process_table() is used if 'Solar Concentrator' is in self.inp

	______________
	Output
	______________

	Non-Depreciable Capital Costs > Land required (acres) > Value
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value
	Planned Replacement > Planned Replacement PEC Cells > Cost ($)
	Planned Replacement > Planned Replacement PEC Cells > Frequency (years)
	Direct Capital Costs - PEC Cells > PEC Cell Cost ($) > Value
	PEC Cells > Number > Value
	'''

	def __init__(photo, self, print_info):
		if 'Solar Concentrator' in self.inp:
			process_table(self.inp, 'Solar Concentrator', 'Value')

		process_table(self.inp, 'Solar Input', 'Value')
		process_table(self.inp, 'Solar-to-Hydrogen Efficiency', 'Value')
		process_table(self.inp, 'PEC Cells', 'Value')
		process_table(self.inp, 'Land Area Requirement', 'Value')
		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')

		photo.hydrogen_production(self)
		photo.PEC_cost(self)
		photo.land_area(self)

		insert(self, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', photo.total_land_area_acres, __name__, print_info = print_info)
		insert(self, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', photo.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(self, 'Planned Replacement', 'Planned Replacement PEC Cells', 'Cost ($)', photo.cell_cost, __name__, print_info = print_info)
		insert(self, 'Planned Replacement', 'Planned Replacement PEC Cells', 'Frequency (years)', self.inp['PEC Cells']['Lifetime (years)']['Value'], __name__, print_info = print_info)

		insert(self, 'Direct Capital Costs - PEC Cells', 'PEC Cell Cost ($)', 'Value', photo.cell_cost, __name__, print_info = print_info)

		insert(self, 'PEC Cells', 'Number', 'Value', photo.cell_number, __name__, print_info = print_info)

	def hydrogen_production(photo, self):

		pec = self.inp['PEC Cells']

		photo.cell_area = pec['Length (m)']['Value'] * pec['Width (m)']['Value']
		cell_insolation = Energy(photo.cell_area * self.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_cell = (cell_insolation.J * self.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		photo.kg_H2_per_cell = (2 * mol_H2_per_cell) / 1000.

	def PEC_cost(photo, self):

		cost_per_cell = photo.cell_area * self.inp['PEC Cells']['Cell Cost ($/m2)']['Value']
		photo.cell_number = np.ceil(self.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / photo.kg_H2_per_cell)
		photo.cell_cost = photo.cell_number * cost_per_cell

	def land_area(photo, self):

		land = self.inp['Land Area Requirement']
		pec = self.inp['PEC Cells']

		photo.total_solar_collection_area = photo.cell_area * photo.cell_number

		cell_plan_view = pec['Length (m)']['Value'] * np.cos(np.radians(land['Cell Angle (degree)']['Value']))
		total_length = cell_plan_view + land['South Spacing (m)']['Value']	
		total_width = pec['Width (m)']['Value'] + land['East/West Spacing (m)']['Value']

		photo.total_land_area = total_width * total_length * photo.cell_number
		photo.total_land_area_acres = photo.total_land_area * 0.000247105
		
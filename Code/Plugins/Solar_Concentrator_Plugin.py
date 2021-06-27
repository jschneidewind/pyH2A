from input_modification import insert, process_table

class Solar_Concentrator_Plugin:
	'''
	______________
	Required Input
	______________

	# Solar Concentrator
	Name | Value
	--- | ---
	Concentration Factor | num
	Cost ($/m2) | num

	process_table() is used

	# PEC Cells
	Name | Value
	--- | ---
	Number | num

	process_table() is used

	# Land Area Requirement
	Name | Value
	--- | ---
	South Spacing (m) | num
	East/West Spacing (m) | 1num

	process_table() is used

	# Non-Depreciable Capital Costs
	Name | Value
	--- | ---
	Solar Collection Area (m2) | num

	process_table() is used
	
	______________
	Output
	______________

	Non-Depreciable Capital Costs > Land required (acres) > Value
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value
	Direct Capital Costs - Solar Concentrator > Solar Concentrator Cost ($) > Value
	'''

	def __init__(conc, self, print_info):
		process_table(self.inp, 'Solar Concentrator', 'Value')
		process_table(self.inp, 'PEC Cells', 'Value')
		process_table(self.inp, 'Land Area Requirement', 'Value')
		process_table(self.inp, 'Non-Depreciable Capital Costs', 'Value')

		conc.land_area(self)
		conc.calculate_cost(self)

		insert(self, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', conc.total_land_area_acres, __name__, print_info = print_info)
		insert(self, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', conc.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(self, 'Direct Capital Costs - Solar Concentrator', 'Solar Concentrator Cost ($)', 'Value', conc.concentrator_cost, __name__, print_info = print_info)

	def land_area(conc, self):

		land = self.inp['Land Area Requirement']

		conc.total_solar_collection_area = self.inp['Solar Concentrator']['Concentration Factor']['Value'] * self.inp['Non-Depreciable Capital Costs']['Solar Collection Area (m2)']['Value']

		conc.total_land_area = land['South Spacing (m)']['Value'] * land['East/West Spacing (m)']['Value'] * self.inp['PEC Cells']['Number']['Value']
		conc.total_land_area_acres = conc.total_land_area * 0.000247105

	def calculate_cost(conc, self):

		conc.concentrator_cost = self.inp['Solar Concentrator']['Cost ($/m2)']['Value'] * conc.total_solar_collection_area

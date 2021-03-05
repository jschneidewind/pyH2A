import numpy as np
from input_modification import insert, process_table

class Multiple_Modules_Plugin:
	''' 
	Simulating mutliple plant modules which are operated together, assuming that only labor cost is reduced  
	calculation of required labor to operate all modules, scaling down labor requirement to one module for calculation

	______________
	Required Input
	______________

	# Technical Operating Parameters and Specification
	Name | Value
	--- | ---
	Plant modules | num

	process_table() is used

	# Non-Depreciable Capital Costs
	Name | Value
	--- | ---
	Solar Collection Area (m2) | num

	process_table() is used

	# Fixed Operating Costs
	Name | Value
	--- | ---
	area | num
	shifts | num
	supervisor | num

	process_table() is used

	______________
	Output
	______________

	Fixed Operating Costs > staff > Value

	''' 

	def __init__(modules, self, print_info):
		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')
		process_table(self.inp, 'Non-Depreciable Capital Costs', 'Value')
		process_table(self.inp, 'Fixed Operating Costs', 'Value')

		modules.required_staff(self)

		insert(self, 'Fixed Operating Costs', 'staff', 'Value', modules.staff_per_module, __name__, print_info = print_info)

	def required_staff(modules, self):
		area = self.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value'] * self.inp['Non-Depreciable Capital Costs']['Solar Collection Area (m2)']['Value']

		staff = np.ceil(area / self.inp['Fixed Operating Costs']['area']['Value']) + self.inp['Fixed Operating Costs']['supervisor']['Value']
		staff = staff * self.inp['Fixed Operating Costs']['shifts']['Value']

		modules.staff_per_module = staff / self.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value']
import numpy as np
from input_modification import insert

class Multiple_Modules_Plugin:

	def __init__(modules, self, print_info):
		modules.required_staff(self)

		insert(self, 'Fixed Operating Costs', 'staff', 'Value', modules.staff_per_module, __name__, print_info = print_info)

	def required_staff(modules, self):

		area = self.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value'] * self.total_solar_collection_area
		staff = np.ceil(area / self.inp['Fixed Operating Costs']['area']['Value']) + self.inp['Fixed Operating Costs']['supervisor']['Value']
		staff = staff * self.inp['Fixed Operating Costs']['shifts']['Value']

		modules.staff_per_module = staff / self.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value']



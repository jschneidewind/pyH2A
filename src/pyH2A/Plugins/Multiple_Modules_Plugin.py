import numpy as np
from pyH2A.Utilities.input_modification import insert, process_table

class Multiple_Modules_Plugin:
	''' Simulating mutliple plant modules which are operated together, assuming that only labor cost is reduced. 
	Calculation of required labor to operate all modules, scaling down labor requirement to one module for subsequent calculations.

	Parameters
	----------
	Technical Operating Parameters and Specification > Plant modules > Value : float or int
		Number of plant modules considered in this calculation, ``process_table()`` is used.
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
		Solar collection area for one plant module in m2, ``process_table()`` is used.
	Fixed Operating Costs > area > Value : float
		Solar collection area in m2 that can be covered by one staffer.
	Fixed Operating Costs > shifts > Value : float or int
		Number of 8-hour shifts (typically 3 for 24h operation).
	Fixed Operating Costs > supervisor > Value : float or int
		Number of shift supervisors.

	Returns
	-------
	Fixed Operating Costs > staff > Value : float
		Number of 8-hour equivalent staff required for operating one plant module.
	''' 

	def __init__(self, dcf, print_info):
		process_table(dcf.inp, 'Technical Operating Parameters and Specifications', 'Value')
		process_table(dcf.inp, 'Non-Depreciable Capital Costs', 'Value')
		process_table(dcf.inp, 'Fixed Operating Costs', 'Value')

		self.required_staff(dcf)

		insert(dcf, 'Fixed Operating Costs', 'staff', 'Value', self.staff_per_module, __name__, print_info = print_info)

	def required_staff(self, dcf):
		'''Calculation of total required staff for all plant modules, then scaling down to staff
		requirements for one module.'''

		area = dcf.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value'] * dcf.inp['Non-Depreciable Capital Costs']['Solar Collection Area (m2)']['Value']

		staff = np.ceil(area / dcf.inp['Fixed Operating Costs']['area']['Value']) + dcf.inp['Fixed Operating Costs']['supervisor']['Value']
		staff = staff * dcf.inp['Fixed Operating Costs']['shifts']['Value']

		self.staff_per_module = staff / dcf.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value']
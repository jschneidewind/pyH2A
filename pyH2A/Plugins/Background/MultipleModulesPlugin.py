import numpy as np
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow

class MultipleModulesPlugin(Plugin):
	''' Simulating mutliple plant modules which are operated together, assuming that only labor cost is reduced. 
	Calculation of required labor to operate all modules, scaling down labor requirement to one module for subsequent calculations.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Plant Modules > Value : float or int
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

	def __init__(
			self, 
			dcf: DiscountedCashFlow
			):
		super().__init__(dcf)

		table_keys = ['Technical Operating Parameters and Specifications', 'Non-Depreciable Capital Costs', 'Fixed Operating Costs']
		self.process_table(table_keys)

		self.required_staff()

		self.process_insert_queue()

	def required_staff(
			self
			) -> None:
		'''Calculation of total required staff for all plant modules, then scaling down to staff
		requirements for one module.'''

		area = self.dcf.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value'] * self.dcf.inp['Non-Depreciable Capital Costs']['Solar Collection Area (m2)']['Value']

		staff = np.ceil(area / self.dcf.inp['Fixed Operating Costs']['area']['Value']) + self.dcf.inp['Fixed Operating Costs']['supervisor']['Value']
		staff = staff * self.dcf.inp['Fixed Operating Costs']['shifts']['Value']

		staff_per_module = staff / self.dcf.inp['Technical Operating Parameters and Specifications']['Plant Modules']['Value']
		self.insert_queue.append(
			{'key': 'Fixed Operating Costs', 'subkey': 'staff', 'value': staff_per_module}
		)
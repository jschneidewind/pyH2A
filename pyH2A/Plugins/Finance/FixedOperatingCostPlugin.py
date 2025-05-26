from pyH2A.Utilities.input_modification import sum_all_tables
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins.Plugin import Plugin


class FixedOperatingCostPlugin(Plugin):
	'''Calculation of yearly fixed operating costs.

	Parameters
	----------
	Fixed Operating Costs > staff > Value : float
		Number of staff, ``process_table()`` is used.
	Fixed Operating Costs > hourly labor cost > Value : float
		Hourly labor cost of staff, ``process_table()`` is used.
	[...] Other Fixed Operating Cost [...] >> Value : float
		Yearly other fixed operating costs, ``sum_all_tables()`` is used.

	Returns
	-------
	[...] Other Fixed Operating Cost [...] > Summed Total > Value : float
		Summed total for each individual table in "Other Fixed Operating Cost" group.
	Fixed Operating Costs > Labor Cost - Uninflated > Value : float
		Yearly total labor cost.
	Fixed Operating Costs > Labor Cost > Value : float
		Yearly total labor cost multiplied by labor inflator.
	Fixed Operating Costs > Total > Value : float
		Sum of total yearly labor costs and yearly other fixed operating costs.
	'''

	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = ['Fixed Operating Costs']
		self.process_table(table_keys)
		self.run_plugin()
		self.process_insert_queue()

	def run_plugin(
			self
			) -> None:
		self.labor_cost()
		self.process_insert_queue()
		self.other_cost()

	def labor_cost(
			self
			) -> None:
		'''Calculation of yearly labor costs by multiplying number of staff times hourly labor cost.'''
		self.labor_uninflated = self.dcf.inp['Fixed Operating Costs']['staff']['Value'] * self.dcf.inp['Fixed Operating Costs']['hourly labor cost']['Value'] * 2080.
		self.labor = self.labor_uninflated * self.dcf.labor_inflator

		self.insert_queue.extend([
			{'key': 'Fixed Operating Costs', 'subkey': 'Labor Cost - Uninflated', 'value': self.labor_uninflated},
			{'key': 'Fixed Operating Costs', 'subkey': 'Labor Cost', 'value': self.labor}
		])
	
	def other_cost(
			self
			) -> None:
		'''Calculation of yearly other fixed operating costs by applying ``sum_all_tables()`` 
		to "Other Fixed Operating Cost" group.'''
		self.other = sum_all_tables(self.dcf.inp, 'Other Fixed Operating Cost', 'Value', insert_total = True, class_object = self.dcf, print_info = self.dcf.print_info) * self.dcf.combined_inflator
		self.insert_queue.append(
			{'key': 'Fixed Operating Costs', 'subkey': 'Total', 'value': self.labor + self.other}
		)
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow

class ProductionScalingPlugin(Plugin):
	'''Calculation of plant output and potential scaling.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value : float
		Plant design capacity in kg of H2/day, ``process_table()`` is used.
	Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value : float
		Operating capacity factor in %, ``process_table()`` is used.
	Technical Operating Parameters and Specifications > Maximum Output at Gate > Value : float, optional
		Maximum output at gate in (kg of H2)/day, ``process_table()`` is used. If this parameter is
		not specified it defaults to `Plant Design Capacity (kg of H2/day)`.
	Technical Operating Parameters and Specifications > New Plant Design Capacity (kg of H2/day) > Value : float, optional
		New plant design capacity in kg of H2/day to calculate scaling, which overwrites possible Scaling Ratio,
		``process_table()`` is used.
	Technical Operating Parameters and Specifications > Scaling Ratio > Value : float, optional
		Scaling ratio which is multiplied by current plant design capacity to obtain scaled plant size,
		``process_table`` is used.
	Technical Operating Parameters and Specifications > Capital Scaling Exponent > Value : float, optional
		Exponent to calculate capital scaling factor, ``process_table()`` is used. Defaults to 0.78.
	Technical Operating Parameters and Specifications > Labor Scaling Exponent > Value : float, optional
		Exponent to calculcate labor scaling factor, ``process_table()`` is used. Defaults to 0.25.

	Returns
	-------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output in (kg of H2)/day.
	Technical Operating Parameters and Specifications > Max Gate Output per Day > Value : float
		Maximum gate ouput in (kg of H2)/day.
	Technical Operating Parameters and Specifications > Output per Year > Value : float
		Yearly output taking operating capacity factor into account, in (kg of H2)/year.
	Technical Operating Parameters and Specifications > Output per Year at Gate > Value	: float
		Actual yearly output at gate, in (kg of H2)/year.
	Technical Operating Parameters and Specifications > Scaling Ratio > Value : float or None
		Returned if New Plant Design Capacity was specified.
	Scaling > Capital Scaling Factor > Value : float or None
		Returned if scaling is active (`Scaling Ratio` or `New Plant Design Capacity (kg of H2/day)` specified).
	Scaling > Labor Scaling Factor > Value : float or None
		Returned if scaling is active (`Scaling Ratio` or `New Plant Design Capacity (kg of H2/day)` specified).

	Notes
	-----
	To scale capital or labor costs, a path to `Scaling > Capital Scaling Factor > Value`
	or `Scaling > Labor Scaling Factor > Value` has to specified for the respective table entry.
	'''

	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = ['Technical Operating Parameters and Specifications']
		self.process_table(table_keys)

		self.dictionary = self.dcf.inp['Technical Operating Parameters and Specifications']

		self.calculate_scaling()
		self.calculate_output()
		self.process_insert_queue()

	def calculate_scaling(
			self
			) -> None:
		'''Calculation of scaling if scaling is requested (either `New Plant Design Capacity (kg of H2/day)` or
		`Scaling Ratio` was provided). Otherwise returns regular design output and output at gate per day in (kg H2).
		'''

		if 'Maximum Output at Gate' not in self.dictionary:
			maximum_output_at_gate = self.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			self.insert_queue.append(
				{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Maximum Output at Gate', 'value': maximum_output_at_gate}
			)
			self.process_insert_queue()
	
		if 'New Plant Design Capacity (kg of H2/day)' in self.dictionary:
			scaling_ratio = self.dictionary['New Plant Design Capacity (kg of H2/day)']['Value'] / self.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			self.insert_queue.append(
				{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Scaling Ratio', 'value': scaling_ratio}
			)

		if 'Scaling Ratio' in self.dictionary:
			self.design_output_per_day = self.dictionary['Plant Design Capacity (kg of H2/day)']['Value'] * self.dictionary['Scaling Ratio']['Value']
			self.max_gate_output_per_day = self.dictionary['Maximum Output at Gate']['Value'] * self.dictionary['Scaling Ratio']['Value']

			if 'Capital Scaling Exponent' in self.dictionary:
				capital_scaling_factor = self.dictionary['Scaling Ratio']['Value'] ** self.dictionary['Capital Scaling Exponent']['Value']
			else:
				capital_scaling_factor = self.dictionary['Scaling Ratio']['Value'] ** 0.78

			if 'Labor Scaling Exponent' in self.dictionary:
				labor_scaling_factor = self.dictionary['Scaling Ratio']['Value'] ** self.dictionary['Labor Scaling Exponent']['Value']
			else:
				labor_scaling_factor = self.dictionary['Scaling Ratio']['Value'] ** 0.25

			self.insert_queue.extend([
				{'key': 'Scaling', 'subkey': 'Capital Scaling Factor', 'value': capital_scaling_factor},
				{'key': 'Scaling', 'subkey': 'Labor Scaling Factor', 'value': labor_scaling_factor}
			])

		else:
			self.design_output_per_day = self.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			self.max_gate_output_per_day = self.dictionary['Maximum Output at Gate']['Value']

		self.insert_queue.extend([
			{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Design Output per Day', 'value': self.design_output_per_day},
			{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Max Gate Output per Day', 'value': self.max_gate_output_per_day}
		])
		
	def calculate_output(
			self
			) -> None:
		'''Calculation of yearly output in kg and yearly output at gate in kg.
		'''

		output_per_year = self.design_output_per_day * 365. * self.dictionary['Operating Capacity Factor (%)']['Value']
		output_per_year_at_gate = self.max_gate_output_per_day * 365. * self.dictionary['Operating Capacity Factor (%)']['Value']
		self.insert_queue.extend([
			{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Output per Year', 'value': output_per_year},
			{'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Output per Year at Gate', 'value': output_per_year_at_gate}
		])
from input_modification import insert, process_table

class Production_Scaling_Plugin:
	'''
	Scaling of capital of labor cost can be implemented by specifying a path to "Scaling > Capital Scaling Factor > Value"
	or "Scaling > Labor Scaling Factor > Value" for the respective table entry.

	If an entire table should be scaled (e.g. a "[...] Direct Capital Cost [...]" table), include a second
	table which uses the "Summed Total" (obtained by sum_all_tables() function) of that table and multiplies
	it by (scaling factor - 1)

	Requires two paths, one to "Summed Total" and one to the respective scaling factor.

	______________
	Required Input
	______________

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Plant Design Capacity (kg of H2/day) | num
	Operating Capacity Factor (%) | num

	process_table() is used

	______________
	Optional Input
	______________
	
	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Maximum Output at Gate | num	
	New Plant Design Capacity (kg of H2/day) | num
	Scaling Ratio | num
	Capital Scaling Exponent | num
	Labor Scaling Exponent | num

	If "Maximum Output at Gate" is not provided it defaults to "Plant Design Capacity (kg of H2/day) > Value"

	If "New Plant Design Capacity (kg of H2/day)" is provided "Scaling Ratio" will be calculated, overwriting 
	"Scaling Ratio" if it already exists.

	"Capital Scaling Exponent" defaults to 0.78 if it is not provided.
	"Labor Scaling Exponent" defaults to 0.25 if it is not provided

	______________
	Output
	______________

	Technical Operating Parameters and Specifications > Design Output per Day > Value
	Technical Operating Parameters and Specifications > Max Gate Output per Day > Value
	Technical Operating Parameters and Specifications > Output per Year > Value
	Technical Operating Parameters and Specifications > Output per Year at Gate > Value	

	if "New Plant Design Capacity (kg of H2/day)" is provided:
		Technical Operating Parameters and Specifications > Scaling Ratio > Value

	if "Scaling Ratio" or "New Plant Design Capacity (kg of H2/day)" is provided:
		Scaling > Capital Scaling Factor > Value
		Scaling > Labor Scaling Factor > Value
	'''

	def __init__(prod, self, print_info):
		process_table(self.inp, 'Technical Operating Parameters and Specifications', 'Value')

		prod.dictionary = self.inp['Technical Operating Parameters and Specifications']

		prod.calculate_scaling(self, print_info)
		prod.calculate_output(self)

		insert(self, 'Technical Operating Parameters and Specifications', 'Design Output per Day', 'Value', prod.design_output_per_day, __name__, print_info = print_info)
		insert(self, 'Technical Operating Parameters and Specifications', 'Max Gate Output per Day', 'Value', prod.max_gate_output_per_day, __name__, print_info = print_info)

		insert(self, 'Technical Operating Parameters and Specifications', 'Output per Year', 'Value', prod.output_per_year, __name__, print_info = print_info)
		insert(self, 'Technical Operating Parameters and Specifications', 'Output per Year at Gate', 'Value', prod.output_per_year_at_gate, __name__, print_info = print_info)

	def calculate_scaling(prod, self, print_info):

		if 'Maximum Output at Gate' not in prod.dictionary:
			maximum_output_at_gate = prod.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			insert(self, 'Technical Operating Parameters and Specifications', 'Maximum Output at Gate', 'Value', maximum_output_at_gate, __name__, print_info = print_info)
	
		if 'New Plant Design Capacity (kg of H2/day)' in prod.dictionary:
			scaling_ratio = prod.dictionary['New Plant Design Capacity (kg of H2/day)']['Value'] / prod.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			insert(self, 'Technical Operating Parameters and Specifications', 'Scaling Ratio', 'Value', scaling_ratio, __name__, print_info = print_info)

		if 'Scaling Ratio' in prod.dictionary:
			prod.design_output_per_day = prod.dictionary['Plant Design Capacity (kg of H2/day)']['Value'] * prod.dictionary['Scaling Ratio']['Value']
			prod.max_gate_output_per_day = prod.dictionary['Maximum Output at Gate']['Value'] * prod.dictionary['Scaling Ratio']['Value']

			if 'Capital Scaling Exponent' in prod.dictionary:
				prod.capital_scaling_factor = prod.dictionary['Scaling Ratio']['Value'] ** prod.dictionary['Capital Scaling Exponent']['Value']
			else:
				prod.capital_scaling_factor = prod.dictionary['Scaling Ratio']['Value'] ** 0.78

			if 'Labor Scaling Exponent' in prod.dictionary:
				prod.labor_scaling_factor = prod.dictionary['Scaling Ratio']['Value'] ** prod.dictionary['Labor Scaling Exponent']['Value']
			else:
				prod.labor_scaling_factor = prod.dictionary['Scaling Ratio']['Value'] ** 0.25

			insert(self, 'Scaling', 'Capital Scaling Factor', 'Value', prod.capital_scaling_factor, __name__, print_info = print_info)
			insert(self, 'Scaling', 'Labor Scaling Factor', 'Value', prod.labor_scaling_factor, __name__, print_info = print_info)

		else:
			prod.design_output_per_day = prod.dictionary['Plant Design Capacity (kg of H2/day)']['Value']
			prod.max_gate_output_per_day = prod.dictionary['Maximum Output at Gate']['Value']

	def calculate_output(prod, self):

		prod.output_per_year = prod.design_output_per_day * 365. * prod.dictionary['Operating Capacity Factor (%)']['Value']
		prod.output_per_year_at_gate = prod.max_gate_output_per_day * 365. * prod.dictionary['Operating Capacity Factor (%)']['Value']
		
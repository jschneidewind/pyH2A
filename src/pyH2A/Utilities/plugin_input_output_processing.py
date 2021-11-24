from input_modification import insert, process_table
import pprint


class Production_Scaling_Plugin:
	"""
	Calculation of plant output and potential scaling.

	If you want to scale capital or labor costs you have to specificy a path to `Scaling > Capital Scaling Factor > Value`
	or `Scaling > Labor Scaling Factor > Value` for the respective table entry.
	...

	Parameters
	----------
    test : test
	[...] Indirect Capital Costs [...] > > Value : float
		`sum_all_tables` is used.
	Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value : float
		Plant design capacity in kg of H2/day, `process_table()` is used.
	Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value : float
		Operating capacity factor in %, `process_table()` is used.
	Technical Operating Parameters and Specifications > Maximum Output at Gate > Value : float, optional
		Maximum output at gate in kg of H2/day, 'process_table()' is used. If this parameter is
		not specified it defaults to `Plant Design Capacity (kg of H2/day)`.
	Technical Operating Parameters and Specifications > New Plant Design Capacity (kg of H2/day) > Value : float, optional
		New plant design capacity in kg of H2/day to calculate scaling, which overwrites possible Scaling Ratio,
		`process_table()` is used.
	Technical Operating Parameters and Specifications > Scaling Ratio > Value : float, optional
		Scaling ratio which is multiplied by current plant design capacity to obtain scaled plant size,
		`process_table` is used.
	Technical Operating Parameters and Specifications > Capital Scaling Exponent > Value : float, optional
		Exponent to calculate capital scaling factor, `process_table()` is used. Defaults to 0.78.
	Technical Operating Parameters and Specifications > Labor Scaling Exponent > Value : float, optional
		Exponent to calculcate labor scaling factor, `process_table()` is used. Defaults to 0.25.

	Returns
	-------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output in kg of H2/day.
	Technical Operating Parameters and Specifications > Max Gate Output per Day > Value : float
		Maximum gate ouput in kg of H2/day.
	Technical Operating Parameters and Specifications > Output per Year > Value : float
		Yearly output taking operating capacity factor into account, in kg H2/year.
	Technical Operating Parameters and Specifications > Output per Year at Gate > Value	: float
		Actual yearly output at gate, in kg H2/year.
	Technical Operating Parameters and Specifications > Scaling Ratio > Value : float or None
		Returned if New Plant Design Capacity was specified.
	Scaling > Capital Scaling Factor > Value : float or None
		Returned if scaling is active (Scaling Ratio or New Plant Design Capacity specified).
	Scaling > Labor Scaling Factor > Value : float or None
		Returned if scaling is active (Scaling Ratio or New Plant Design Capacity specified).
	"""
	
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



def detect_parameters_and_output(line):
	""""Detection of parameters and output values in line based on presence of more than one tab
	or more than four spaces"""

	if '\t\t' in line: #or '     ' in line:
		return False
	else:
		return True

def process_single_line(line, output_dict):

	if detect_parameters_and_output(line):

		complete_string = line.split(':')
		variable_string = complete_string[0].strip(', \t')
		variable_type = complete_string[1].strip(', \t')

		output_dict[variable_string] = variable_type

def extract_input_output_from_docstring(plugin_name):

	doc_string = plugin_name.__doc__.split('\n')

	parameters_dict = {}
	output_dict = {}

	parameters = False
	output = False

	for counter, line in enumerate(doc_string):

		if '---' in line and 'Parameters' in doc_string[counter-1]:
			parameters = True

		if '---' in line and 'Returns' in doc_string[counter-1]:
			parameters = False
			output = True
	
		if line == '' or line == '\t':
			parameters = False
			output = False

		if parameters and '---' not in line:
			process_single_line(line, parameters_dict)

		if output and '---' not in line:
			process_single_line(line, output_dict)


	print(output_dict)




extract_input_output_from_docstring(Production_Scaling_Plugin)
		
import types
import importlib.machinery
import copy
import sys
import numpy as np
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12
import find_nearest as fn
from input_modification import parse_parameter, process_input, process_table, insert

import pprint

from timeit import default_timer as timer


'''Printing actions of plugins (and sensitivity analysis?)'''

def num(s):
	s = s.replace(',', '')

	if s[-1] == '%' and ';' not in s:
		return num(s[:-1])/100.
	else:
		try:
			return int(s)
		except ValueError:
			try:
				return float(s)
			except ValueError:
				return str(s)

def convert_input_to_dictionary(file):

	inp = {}
	table = False
	header = False

	with open(file, 'r') as file_read:
		for line in file_read:
			
			if line[0] == '#':
				variable_name = line.strip(' #\n')
				inp[variable_name] = {}
				header = False

			if line.strip(' ') == '\n':
				table = False
				header = True

			if line[0] == '-':
				table = True
				header = False

			if header is True and line.strip(' ') != '\n':
				header_entries = line.split('|')

			if table is True and line[0] != '-':
				table_entries = line.split('|')
				inp[variable_name][table_entries[0].strip(' ')] = {}

				for i in zip(header_entries[1:], table_entries[1:]):
					header_entry = i[0].strip(' \n')
					table_entry = num(i[1].strip(' \n'))
					inp[variable_name][table_entries[0].strip(' ')][header_entry] = table_entry 

	return inp

def parse_file_name(name):

	file_name = name.split('/')
	file_name = file_name[-1].split('.')

	return file_name[0]

def npv(rate, values):

	return (values / (1+rate)**np.arange(1, len(values)+1)).sum(axis=0)

def make_bold(string):
	string = string.split(' ')

	output = ''

	for word in string:
		output += r'$\bf{' + word + '}$' + ' '

	return output

class Figure:

	def __init__(self, function, directory):
		self.function = function
		self.directory = directory
		self.name = self.function.__name__
		self.fig = function()

	def show(self):

		plt.show()

	def save(self):

		self.fig.savefig('{0}{1}.png'.format(self.directory, self.name), transparent = True, dpi = 150)

class Discounted_Cash_Flow:
	'''
    ___________________
	General Remarks
    ___________________

    # Numerical Inputs

    Numbers use decimal points. Commas can be used as thousands seperator, they are removed from numbers
    during processing. the "%" can be used after a number, indicating that it will be divided by 100
    before being used. 

    # Special symbols

    Tables in the input file are formatted using GitHub flavoured Markdown. 
    This means that "#" at the beginning of a line indicates a header.
    "|" is used to seperate columns.
    "---" is used on its own line to seperate table headers from table entries.

    Paths to locations in the input file/in self.inp are specified using ">". Paths are always composed
    of three levels: top key > middle key > bottom key.

    File name paths are specified using "/".

    In cases where multiple numbers are used in one field (e.g. during sensitivity analysis), these numbers
    are seperated using ";".

	# Order in the input file

	Order matters in the following cases: 

	1. For the "Workflow" table the order of entries determines the order
	in which functions and plugins are executed.

	2. For a group of sum_all_tables() processed tables (sharing the specified part of their key, e.g. "Direct
	Capital Cost"), they are processed in their provided order.

	3. Within a table, the first column will be used to generate the "middle key" of self.inp. The order of the
	other columns is not important.

	# Input

	Processed input cells can contain either a number or path(s) (if multiple paths are used, they have to
	be seperated by ";") to other cells. The use of process_input() (and hence, process_table(), sum_table() and 
	sum_all_tables()) also allows for the value of an input cell to be multiplied by another cell by including
	path(s) in an additiona column (column name typically "Path").


	______________
	Required Input
	______________

	# Workflow
	Name | Type
	--- | ---
	initial_equity_depreciable_capital | function
	non_depreciable_capital_costs | function
	replacement_costs | function
	fixed_operating_costs | function
	variable_operating_costs | function

	Optional:

	Inclusion of plugins via

	plugin_name | plugin

	Workflow specifies which functions and plugins are used and in which order they are executed. The listed
	five functions have to be executed in the specified order for pyH2A to work. Plugins can be inserted at 
	appropiate positions (Type: "plugin"). Plugins have to be located in the ./Plugins/ directory. 

	Plugins needs to be composed of a class with the same name as the plugin file name. This class uses two inputs, 
	a discounted cash flow object (usually indicated by "self") and "print_info", which controls the printing of run time
	statements. Within the __init__ function of the class the actions of the plugins are specified, typically call(s)
	of the "insert()" function to modify the discounted cash flow object's "inp" dictionary (self.inp).

	# Technical Operating Parameters and Specifications
	Name | Value
	--- | ---
	Output per Year at Gate | num

	process_input() is used

	# Financial Input Values
	Name | Value
	--- | ---
	ref year | num
	startup year | num
	basis year | num
	current year capital costs | num
	startup time | num
	plant life | num
	analysis period | num
	depreciation length | num
	depreciation type | MACRS   # other types not yet implemented
	equity | num
	interest | num
	debt | Constant      # other debt not yet implemented
	startup cost fixed | num
	startup revenues | num
	startup cost variable | num
	decommissioning | num
	salvage | num
	inflation | num
	irr | num
	state tax | num
	federal tax | num
	working capital | num

	process_table() is used on "Financial Input Values"

	# Construction
	Name | Value
	--- | ---
	str | num (have to sum to 100%)

	process_table() is used

	Number of entries in construction determines construction period in years (each entry corresponds to one year).
	Have to be in order (entry 0 corresponds to first construction years, entry 2 the second etc.)
	"Value" refers to % of capital spent in corresponding construction year, all values have to sum to 100%.

	# Depreciable Capital Costs
	Name | Value
	--- | ---
	Inflated | num

	process_input() is used

	# Non-Depreciable Capital Costs
	Name | Value
	--- | ---
	Inflated | num

	process_input() is used

	# Replacement
	Name | Value
	--- | ---
	Total | num

	# Fixed Operating Costs
	Name | Value
	--- | ---
	Total | num

	process_input() is used

	# Variable Operating Costs
	Name | Value
	--- | ---
	Total | num

	______________
	Output
	______________

	Discounted_Cash_Flow class object.

	.h2_cost attribute (H2 cost per kg)
	.contributions attribute (cost contributions to H2 price)
	.plugs dictionary containing plugin class objects used during analysis

	'''

	def __init__(self, input_file, print_info = True, check_processing = True):
		if isinstance(input_file, str):
			self.inp = convert_input_to_dictionary(input_file)
		else:
			self.inp = input_file

		self.print_info = print_info

		process_table(self.inp, 'Financial Input Values', 'Value')
		self.fin = self.inp['Financial Input Values']

		self.npv_dict = {}	
		self.plugs = {}

		self.time()
		self.inflation()

		self.workflow(self.inp, self.npv_dict, self.plugs)

		self.npv_dict['salvage'], self.npv_dict['decomissioning'] = self.salvage_decommissioning()		
		self.npv_dict['working_capital_reserve'] = self.working_capital_reserve_calc()
		self.npv_dict['interest'], self.npv_dict['principal_payment'] = self.debt_financing()
		self.npv_dict['depreciation_charge'] = self.depreciation_charge()
		self.npv_dict['h2_sales'] = self.h2_sales()
		self.h2_cost()
		self.npv_dict['revenue'] = self.h2_revenue()
		self.npv_dict['pre_depreciation_income'], self.npv_dict['taxable_income'], self.npv_dict['taxes'], self.npv_dict['after_tax_income'] = self.income()
		self.cash_flow()
		self.cost_contribution()

		if check_processing is True:
			self.check_processing()

	def workflow(self, input, npv_dict, plugs_dict):

		for key in input['Workflow']:
			if input['Workflow'][key]['Type'] == 'function':
				self.execute_function(key, npv_dict)
			else:
				self.execute_plugin(key, plugs_dict)

	def execute_function(self, function_name, npv_dict):
		'''Execute class function named "function_name" and store output in "npv_dict"'''

		called_function = getattr(self, function_name)
		output = called_function()
		npv_dict[function_name] = output

	def execute_plugin(self, plugin_name, plugs_dict):
		loader = importlib.machinery.SourceFileLoader(plugin_name, './Plugins/{0}.py'.format(plugin_name))
		mod = types.ModuleType(loader.name)
		loader.exec_module(mod)

		plugin_class = getattr(mod, plugin_name)
		plugin_object = plugin_class(self, self.print_info)

		plugs_dict[plugin_name] = plugin_object

	def time(self):

		insert(self, 'Financial Input Values', 'construction time', 'Value', len(self.inp['Construction']), __name__, print_info = self.print_info)

		construction_start = self.fin['startup year']['Value'] - self.fin['construction time']['Value']
		end_of_life = self.fin['startup year']['Value'] + self.fin['plant life']['Value']

		self.years = np.arange(construction_start, end_of_life)
		self.analysis_years = np.arange(0, self.fin['construction time']['Value'] + self.fin['plant life']['Value'])
		self.plant_years = np.arange(-self.fin['construction time']['Value'], self.fin['plant life']['Value'])

	def inflation(self):

		inflation_rate = 1 + self.fin['inflation']['Value']
		self.inflation_factor = inflation_rate ** self.plant_years
		self.inflation_correction = inflation_rate ** (self.fin['startup year']['Value'] - self.fin['ref year']['Value'])

		plant_cost = np.genfromtxt('../Lookup_Tables/Plant_Cost_Index.csv', delimiter = '	')
		gdp_deflator_price = np.genfromtxt('../Lookup_Tables/GDP_Implicit_Deflator_Price_Index.csv', delimiter = '	')
		labor_price = np.genfromtxt('../Lookup_Tables/Labor_Index.csv', delimiter = '	')
		chemical_price = np.genfromtxt('../Lookup_Tables/SRI_Chemical_Price_Index.csv', delimiter = '	')

		plant_idx = fn.find_nearest(plant_cost, [self.fin['current year capital costs']['Value'], self.fin['basis year']['Value']])
		gdp_idx = fn.find_nearest(gdp_deflator_price, [self.fin['ref year']['Value'], self.fin['current year capital costs']['Value']])
		labor_idx = fn.find_nearest(labor_price, [self.fin['ref year']['Value'], self.fin['basis year']['Value']])
		chemical_idx = fn.find_nearest(chemical_price, [self.fin['ref year']['Value'], self.fin['basis year']['Value']])

		self.cepci_inflator = plant_cost[:,1][plant_idx[0]]/plant_cost[:,1][plant_idx[1]]
		self.ci_inflator = gdp_deflator_price[:,1][gdp_idx[0]]/gdp_deflator_price[:,1][gdp_idx[1]]
		self.combined_inflator = self.cepci_inflator * self.ci_inflator
		self.labor_inflator = labor_price[:,1][labor_idx[0]]/labor_price[:,1][labor_idx[1]]
		self.chemical_inflator = chemical_price[:,1][chemical_idx[0]]/chemical_price[:,1][chemical_idx[1]]

	def production_scaling(self):

		self.output_per_year_at_gate = process_input(self.inp, 'Technical Operating Parameters and Specifications', 'Output per Year at Gate', 'Value')

		return 0.

	def initial_equity_depreciable_capital(self):

		self.depreciable_capital = process_input(self.inp, 'Depreciable Capital Costs', 'Inflated', 'Value')
		self.depreciable_capital_inflation = self.depreciable_capital * self.inflation_correction

		process_table(self.inp, 'Construction', 'Value')

		construction_years = []
		for counter, key in enumerate(self.inp['Construction']):
			cost = self.inp['Construction'][key]['Value'] * self.fin['equity']['Value'] * self.depreciable_capital_inflation * self.inflation_factor[counter]
			construction_years.append(cost)

		self.initial_depreciable_capital = np.sum(construction_years)

		self.annual_initial_depreciable_capital = np.zeros(len(self.inflation_factor))
		self.annual_initial_depreciable_capital[:self.fin['construction time']['Value']] = construction_years

		self.after_tax_nominal_irr = (1 + self.fin['irr']['Value']) * (1 + self.fin['inflation']['Value']) - 1

		return np.npv(self.after_tax_nominal_irr, construction_years)

	def non_depreciable_capital_costs(self):
		'''Land required only scales when Photocatalytic_Plugin is used'''

		self.non_depreciable_capital = process_input(self.inp, 'Non-Depreciable Capital Costs', 'Inflated', 'Value')
		self.non_depreciable_capital_inflated = self.non_depreciable_capital * self.inflation_correction
		non_depreciable_capital_inflation_corrected = self.non_depreciable_capital_inflated * self.inflation_factor[0]

		self.annual_non_depreciable_capital = np.zeros(len(self.inflation_factor))
		self.annual_non_depreciable_capital[0] = non_depreciable_capital_inflation_corrected

		return non_depreciable_capital_inflation_corrected

	def replacement_costs(self):
	
		yearly_costs = self.inp['Replacement']['Total']['Value']

		self.start_idx = fn.find_nearest(self.plant_years, 0)[0]
		yearly_costs[:self.start_idx] = 0
		self.annual_replacement_costs = yearly_costs	

		return np.npv(self.after_tax_nominal_irr, yearly_costs)

	def salvage_decommissioning(self):

		self.total_capital_inflated = self.depreciable_capital_inflation + self.non_depreciable_capital_inflated

		decommissioning = self.depreciable_capital_inflation * self.fin['decommissioning']['Value']
		salvage = self.total_capital_inflated * self.fin['salvage']['Value']

		self.decommissioning_costs = np.zeros(len(self.plant_years))
		self.decommissioning_costs[-1] = decommissioning * self.inflation_factor[-1]

		self.salvage_income = np.zeros(len(self.plant_years))
		self.salvage_income[-1] = salvage * self.inflation_factor[-1]

		return np.npv(self.after_tax_nominal_irr, self.salvage_income), np.npv(self.after_tax_nominal_irr, self.decommissioning_costs)

	def fixed_operating_costs(self):
		'''Fixed operating costs repair should scale'''

		fixed_operating = process_input(self.inp, 'Fixed Operating Costs', 'Total', 'Value')
		fixed_operating_inflated = fixed_operating * self.inflation_correction

		self.start_up_time_idx = self.start_idx + self.fin['startup time']['Value']

		yearly_costs = fixed_operating_inflated * self.inflation_factor
		yearly_costs[:self.start_up_time_idx] = yearly_costs[:self.start_up_time_idx] * self.fin['startup cost fixed']['Value']
		yearly_costs[:self.start_idx] = 0

		self.fixed_operating_costs = yearly_costs

		return np.npv(self.after_tax_nominal_irr, yearly_costs)

	def variable_operating_costs(self):

		variable_operating_costs = self.inflation_factor * self.inp['Variable Operating Costs']['Total']['Value']
		variable_operating_costs[:self.start_up_time_idx] = variable_operating_costs[:self.start_up_time_idx] * self.fin['startup cost variable']['Value']
		variable_operating_costs[:self.start_idx] = 0

		self.variable_operating_costs = variable_operating_costs

		return np.npv(self.after_tax_nominal_irr, variable_operating_costs)

	def working_capital_reserve_calc(self):

		sum_variable_fixed_operating_costs = self.variable_operating_costs + self.fixed_operating_costs

		self.working_capital_reserve = -self.fin['working capital']['Value'] * np.diff(sum_variable_fixed_operating_costs)
		self.working_capital_reserve[-1] = -np.sum(self.working_capital_reserve[:-1])
		self.working_capital_reserve = np.r_[np.zeros(1), self.working_capital_reserve]

		return -np.npv(self.after_tax_nominal_irr, self.working_capital_reserve)

	def debt_financing(self):
		'''Assumption of constant debt financing'''

		self.debt_financed_capital = self.depreciable_capital_inflation * (1 - self.fin['equity']['Value']) * self.inflation_factor[0]
		interest = self.debt_financed_capital * self.fin['interest']['Value']
		self.interest_per_year = np.ones(len(self.inflation_factor)) * interest

		self.principal_payment = np.zeros(len(self.inflation_factor))
		self.principal_payment[-1] = self.debt_financed_capital

		return np.npv(self.after_tax_nominal_irr, self.interest_per_year), np.npv(self.after_tax_nominal_irr, self.principal_payment)

	def depreciation_charge(self):

		end_idx = len(self.plant_years)	

		macrs = np.genfromtxt('../Lookup_Tables/MACRS.csv', delimiter = '	')   # only MACRS depreciation
		macrs[1:,1:] = macrs[1:,1:]/100.
		idx_macrs = fn.find_nearest(macrs[0][1:], self.fin['depreciation length']['Value'])[0] 
		macrs_values = macrs[1:,1:][:,idx_macrs]
		macrs_values = macrs_values[macrs_values != 0]

		total_initial_depreciable_capital = self.debt_financed_capital + self.initial_depreciable_capital
		annual_depreciable_capital = np.copy(self.annual_replacement_costs)
		annual_depreciable_capital[self.start_idx] += total_initial_depreciable_capital

		depreciation = np.outer(annual_depreciable_capital, macrs_values)

		charge = []
		diagonals = sum(depreciation.shape) + 1

		for i in range(1, diagonals):
			a = np.arange(0, i)
			b = a[::-1]
			c = np.c_[a, b]

			idx = c[(c[:,0] <= depreciation.shape[0] - 1) & (c[:,1] <= depreciation.shape[1] - 1)]
			idx = (np.array(idx[:,0]), np.array(idx[:,1]))

			diagonal = depreciation[idx]
			charge.append(np.sum(diagonal))

		charge = np.asarray(charge)

		self.annual_charge = charge[:end_idx]
		self.annual_charge[-1] += np.sum(charge[end_idx:])

		return np.npv(self.after_tax_nominal_irr, self.annual_charge)

	def h2_sales(self):

		self.annual_sales = np.ones(len(self.inflation_factor)) * self.output_per_year_at_gate
		self.annual_sales[:self.start_up_time_idx] = self.annual_sales[:self.start_up_time_idx] * self.fin['startup revenues']['Value']
		self.annual_sales[:self.start_idx] = 0

		return np.npv(self.fin['irr']['Value'], self.annual_sales)

	def h2_cost(self):

		self.total_tax_rate = self.fin['federal tax']['Value'] + self.fin['state tax']['Value'] * (1. - self.fin['federal tax']['Value'])

		lcoe_capital_costs = self.npv_dict['initial_equity_depreciable_capital'] + self.npv_dict['non_depreciable_capital_costs'] + self.npv_dict['replacement_costs'] + self.npv_dict['working_capital_reserve']
		lcoe_depreciation = -self.npv_dict['depreciation_charge'] * self.total_tax_rate
		lcoe_principal_payment = self.npv_dict['principal_payment']
		lcoe_operating_costs = (-self.npv_dict['salvage'] + self.npv_dict['decomissioning'] + self.npv_dict['fixed_operating_costs'] + self.npv_dict['variable_operating_costs'] + self.npv_dict['interest']) * (1. - self.total_tax_rate)

		lcoe_h2_sales = self.npv_dict['h2_sales'] * (1. - self.total_tax_rate)

		# print('Capital Cost:', lcoe_capital_costs)
		# print('Depreciation:', lcoe_depreciation)
		# print('Principal Payment:', lcoe_principal_payment)
		# print('Operating Costs:', lcoe_operating_costs)
		# print('H2 Sales:', lcoe_h2_sales)

		self.h2_cost_nominal = (lcoe_capital_costs + lcoe_depreciation + lcoe_principal_payment + lcoe_operating_costs)/lcoe_h2_sales * (1. + self.fin['inflation']['Value']) ** self.fin['construction time']['Value']
		self.h2_cost = self.h2_cost_nominal/self.inflation_correction

	def h2_revenue(self):

		self.annual_revenue = self.annual_sales * self.h2_cost_nominal * self.inflation_factor

		return np.npv(self.after_tax_nominal_irr, self.annual_revenue)

	def income(self):

		self.annual_pre_depreciation_income = self.annual_revenue + self.salvage_income - self.decommissioning_costs - self.fixed_operating_costs - self.variable_operating_costs - self.interest_per_year
		self.taxable_income = self.annual_pre_depreciation_income - self.annual_charge
		
		self.annual_taxes = self.taxable_income * self.total_tax_rate

		self.after_tax_income = self.annual_pre_depreciation_income - self.annual_taxes

		return np.npv(self.after_tax_nominal_irr, self.annual_pre_depreciation_income), np.npv(self.after_tax_nominal_irr, self.taxable_income), np.npv(self.after_tax_nominal_irr, self.annual_taxes), np.npv(self.after_tax_nominal_irr, self.after_tax_income)

	def cash_flow(self):

		pre_tax_cash_flow = -self.annual_initial_depreciable_capital - self.annual_replacement_costs + self.working_capital_reserve - self.annual_non_depreciable_capital + self.annual_pre_depreciation_income - self.principal_payment
		after_tax_post_depreciation_cash_flow = pre_tax_cash_flow - self.annual_taxes
		cummulative_cash_flow = np.cumsum(after_tax_post_depreciation_cash_flow)

		return np.npv(self.after_tax_nominal_irr, cummulative_cash_flow)

	def cost_contribution(self):

		revenue = self.expenses_per_kg_H2(self.npv_dict['revenue'])

		self.contributions = {'Initial equity depreciable capital': self.expenses_per_kg_H2(self.npv_dict['initial_equity_depreciable_capital']),
						      'Non-depreciable capital' : self.expenses_per_kg_H2(self.npv_dict['non_depreciable_capital_costs']),
						 	  'Replacement costs' : self.expenses_per_kg_H2(self.npv_dict['replacement_costs']),
						      'Salvage' : -self.expenses_per_kg_H2(self.npv_dict['salvage']),
						 	  'Decomissioning' : self.expenses_per_kg_H2(self.npv_dict['decomissioning']),
						  	  'Fixed operating costs' : self.expenses_per_kg_H2(self.npv_dict['fixed_operating_costs']),
						 	  'Variable operating costs' : self.expenses_per_kg_H2(self.npv_dict['variable_operating_costs']),
						 	  'Working capital reserve' : self.expenses_per_kg_H2(self.npv_dict['working_capital_reserve']),
						   	  'Interest' : self.expenses_per_kg_H2(self.npv_dict['interest']),
						      'Principal payment' : self.expenses_per_kg_H2(self.npv_dict['principal_payment']),
						      'Taxes' : self.expenses_per_kg_H2(self.npv_dict['taxes'])}

	def expenses_per_kg_H2(self, value):

		return value/self.npv_dict['h2_sales'] * (1. + self.fin['inflation']['Value']) ** self.fin['construction time']['Value'] / self.inflation_correction

	def check_processing(self):

		exceptions = ['Workflow', 'Sensitivity Analysis']

		for top_key in self.inp:
			if top_key not in exceptions:
				for middle_key in self.inp[top_key]:
					if 'Processed' not in self.inp[top_key][middle_key]:
						print('Warning: "{0} > {1}" has not been processed'.format(top_key, middle_key))

class Sensitivity_Analysis:
	'''

	Sensitivty analysis for multiple entries: sensitivity parameter (specified in its own table), which is referenced by desired entries
	In sensitivity analysis, that sensitivty parameter is then varied.

	______________
	Required Input
	______________

	# Sensitivity Analysis
	Parameter | Name | Type | Values
	--- | --- | --- | ---
	str | str | value or factor | num (delimited by ";")

	"Parameter" is a ">" delimited string that points to a location of the input file via
	top_key > middle_key > bottom_key

	"Name" is the parameter name displayed in the output plot.

	"Type" is either 'value' or 'factor'. If Type == value, the entered "Values" are used as is.
	if Type == factor, the entered "Values" are multiplied by the location value.

	"Values" is a ";" delimited string, an arbitrary number of values can be entered, but typcically two are used for
	sensitivity analysis.	

	______________
	Output
	______________

	Sensitivity_Analysis class object with attributes used for plot generation.

	'''

	def __init__(self, input_file):
		self.inp = convert_input_to_dictionary(input_file)
		self.results = self.perform_sensitivity_analysis()

	def perform_sensitivity_analysis(self):

		sensitivity_results = {}

		for key in self.inp['Sensitivity Analysis']:
			parameters = parse_parameter(key)
			name = self.inp['Sensitivity Analysis'][key]['Name']

			sensitivity_results[name] = {}
			sensitivity_results[name]['Base'] = self.inp[parameters[0]][parameters[1]][parameters[2]]
			sensitivity_results[name]['Values'] = {}

			values = parse_parameter(self.inp['Sensitivity Analysis'][key]['Values'], delimiter = ';')

			for value in values:
				input_dict = copy.deepcopy(self.inp)
				numerical_value = num(value)

				if self.inp['Sensitivity Analysis'][key]['Type'] == 'factor':
					input_dict[parameters[0]][parameters[1]][parameters[2]] *= numerical_value
					sensitivity_results[name]['Base'] = '1.0x'
					shown_value = '{0}x'.format(numerical_value)
				else:
					input_dict[parameters[0]][parameters[1]][parameters[2]] = numerical_value
					shown_value = value

					if '%' in shown_value:
							sensitivity_results[name]['Base'] = '{0}%'.format(self.inp[parameters[0]][parameters[1]][parameters[2]] * 100)

				dcf = Discounted_Cash_Flow(input_dict, print_info = False)

				sensitivity_results[name]['Values'][shown_value] = dcf.h2_cost

		return sensitivity_results

class Output:

	def __init__(self, input_file, output_directory, print_info = False):
		self.print_info = print_info
		self.input_file = input_file
		self.file_name = parse_file_name(self.input_file)
		self.output_directory = output_directory

		self.base_case = Discounted_Cash_Flow(self.input_file, print_info = self.print_info)

		cost_breakdown_figure = Figure(self.cost_breakdown, self.output_directory)
		cost_breakdown_figure.save()

		try:
			sensitivity_figure = Figure(self.sensitivity_box_plot, self.output_directory)
			sensitivity_figure.save()
		except KeyError:
			print('KeyError, sensitivity analysis not performed.')
			pass

		self.report()

	def cost_breakdown(self, label_offset = 8.5):

		sorted_keys = sorted(self.base_case.contributions, key = self.base_case.contributions.get)
		sorted_contributions = {}

		for key in sorted_keys:
			sorted_contributions[key] = self.base_case.contributions[key]

		fig, ax = plt.subplots()
		fig.subplots_adjust(left = 0.4)
		ax.set_xlabel(r'Levelized cost / USD per kg $H_{2}$')
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2)
		cmap = plt.get_cmap('plasma')

		label_offset = self.base_case.h2_cost / label_offset

		for counter, key in enumerate(sorted_contributions):
			value = sorted_contributions[key]

			color_value = counter / len(sorted_contributions)
			ax.barh(key, sorted_contributions[key], color = cmap(color_value))
			ax.annotate('${:.2f}'.format(value), xy = (value + label_offset, counter), va = 'center', ha = 'center')

		ax.barh(make_bold('Total cost of hydrogen'), self.base_case.h2_cost, color = 'darkgreen')
		ax.annotate('${:.2f}'.format(self.base_case.h2_cost), xy = (self.base_case.h2_cost + label_offset, len(sorted_contributions)), va = 'center', ha = 'center')

		xlim = np.asarray(ax.get_xlim())
		xlim[1] += 2 * label_offset
		ax.set_xlim(xlim)

		return fig 

	def sensitivity_box_plot(self, height = 0.8, label_offset = 0.1, lim_extra = 0.2):

		self.sensitivity = Sensitivity_Analysis(self.input_file)
		data = self.sensitivity.results

		fig, ax = plt.subplots(figsize = (7.5, 4))
		fig.subplots_adjust(left = 0.45, bottom = 0.2, right = 0.99, top = 0.95)

		number_of_entries = len(data)
		base_case = self.base_case.h2_cost
		data_array, sensitivity_array, name_array, base_array = self.sort_sensitivity_data(data)

		x_width = np.amax(data_array) - np.amin(data_array)
		label_offset = x_width * label_offset
		extra = x_width * lim_extra

		xlim = [np.amin(data_array) - extra, np.amax(data_array) + extra]
		ylim = [-height, number_of_entries]	

		for counter, row in enumerate(data_array):
			lower = row[0]
			upper = row[1]

			rectangle_left = patches.Rectangle((lower, counter-height/2), base_case - lower, height, edgecolor = 'none', facecolor = 'darkgreen')
			rectangle_right = patches.Rectangle((base_case, counter-height/2), upper - base_case, height, edgecolor = 'none', facecolor = 'darkred')

			ax.add_patch(rectangle_left)
			ax.add_patch(rectangle_right)

			ax.annotate('${:.2f}'.format(lower), xy = (lower - label_offset, counter), va = 'center', ha = 'center')
			ax.annotate('${:.2f}'.format(upper), xy = (upper + label_offset, counter), va = 'center', ha = 'center')

		labels = []

		for counter, name in enumerate(name_array):
			labels.append('{0}\n{1}, {2}, {3}'.format(make_bold(name), sensitivity_array[counter][0], base_array[counter], sensitivity_array[counter][1]))

		ax.set_xlabel(r'Cost sensitivity / USD per kg $H_{2}$')
		ax.set_yticks(np.arange(0, number_of_entries))
		ax.set_yticklabels(labels)
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2)

		ax.set_xlim(xlim[0], xlim[1])
		ax.set_ylim(ylim[0], ylim[1])
		ax.plot((base_case, base_case), (ylim[0], ylim[1]), '--', color = 'black')	

		return fig

	def sort_sensitivity_data(self, data):

		name_list = list(data)
		name_array = np.asarray(name_list)
		data_array = []
		sensitivity_array = []
		base_array = []

		for key in data:
			sensitivities = list(data[key]['Values'])
			sensitivity_array.append(sensitivities)
			base_array.append(data[key]['Base'])
			data_array.append([data[key]['Values'][sensitivities[0]], data[key]['Values'][sensitivities[1]]])

		data_array = np.asarray(data_array)
		sensitivity_array = np.asarray(sensitivity_array)
		base_array = np.asarray(base_array)

		idx_sort_row = np.argsort(data_array)

		for counter, idx in enumerate(idx_sort_row):
			data_array[counter] = data_array[counter][idx]
			sensitivity_array[counter] = sensitivity_array[counter][idx]

		idx_sort = np.argsort(data_array[:,1])

		data_array = data_array[idx_sort]
		sensitivity_array = sensitivity_array[idx_sort]
		name_array = name_array[idx_sort]
		base_array = base_array[idx_sort]

		return data_array, sensitivity_array, name_array, base_array

	def report(self):

		pdf = FPDF()
		pdf.set_margins(left = 20, top = 20, right = 20)
		pdf.add_page()
		pdf.set_draw_color(211, 218, 219)	
		
		pdf.set_font('helvetica', 'B', 20)
		pdf.cell(0, 0, 'Total Hydrogen Cost', 0, 2)
		pdf.line(20, 25, 190, 25)
		pdf.cell(0, 10, '', 0, 2)

		pdf.set_font('helvetica', 'B', 12)

		pdf.cell(40, 10, 'Name', 1, 0, 'C')
		pdf.cell(40, 10, 'Value', 1, 2, 'C')

		pdf.cell(-40)
		pdf.set_font('helvetica', '', 12)
		pdf.cell(40, 10, 'Total Cost ($/kg)', 1, 0, 'C')
		pdf.cell(40, 10, '${:.5f}'.format(self.base_case.h2_cost), 1, 2, 'C')

		pdf.set_font('helvetica', 'B', 20)
		pdf.cell(-40, 10, '', 0, 1)
		pdf.cell(0, 0, 'Graphs', 0, 2)	
		pdf.line(20, 65, 190, 65)

		pdf.image('{0}cost_breakdown.png'.format(self.output_directory) , None, None, w = 150, h = 0)

		pdf.cell(0, 3, '', 0, 2)
		pdf.set_font('helvetica', 'B', 10)
		pdf.cell(15, 0, 'Figure 1', 0, 0)
		pdf.set_font('helvetica', '', 10)
		pdf.cell(0, 0, 'Cost contributions to total hydrogen cost.', 0, 2)

		try:
			pdf.cell(-70, 5, '', 0, 1)
			pdf.image('{0}sensitivity_box_plot.png'.format(self.output_directory) , None, None, w = 170, h = 0)

			pdf.set_font('helvetica', 'B', 10)	
			pdf.cell(15, 0, 'Figure 2', 0, 0)	
			pdf.set_font('helvetica', '', 10)
			pdf.cell(0, 0, 'Sensitivity of hydrogen cost to different parameters.', 0, 2)
		except FileNotFoundError:
			print('Sensitivity plot not found, not added to report.')
			pass

		pdf.output('{0}{1}.pdf'.format(self.output_directory, self.file_name), 'F')

def run_pyH2A():

	path_to_input = sys.argv[1]
	path_to_output = sys.argv[2] 

	output = Output(path_to_input, path_to_output)
	
def main():

	# dcf = Discounted_Cash_Flow('../Input/210222_Current_Natural_Gas.md', print_info = False)
	# print(dcf.h2_cost)

	#pprint.pprint(dcf.inp['Unplanned Replacement'])

	# #pprint.pprint(dcf.inp['Unplanned Replacement'])

	#pprint.pprint(dcf.inp)

	#start = timer()

	# dcf = Discounted_Cash_Flow('../Input/Future_PEC_Type_1.md', print_info = False)

	# #end = timer()

	# #print(end - start)

	# print(dcf.h2_cost)


	#pprint.pprint(dcf.inp['Utilities'])


	#pprint.pprint(dcf.inp['Direct Capital Costs - Gas Processing'])
	#pprint.pprint(dcf.inp['Direct Capital Costs - Installation Costs'])



	# sensitivity = Sensitivity_Analysis('../Input/Future_PEC_Type_2.md')
	# print(sensitivity.results)

	output = Output('../Input/210222_Current_Natural_Gas.md', '../Output/210222_Current_Natural_Gas/')
	print(output.base_case.h2_cost)



	#plt.show()

	#run_pyH2A()

if __name__ == '__main__':
	main()
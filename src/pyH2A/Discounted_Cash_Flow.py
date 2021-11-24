import copy
import numbers
from functools import lru_cache
import numpy as np

from pyH2A.Utilities.input_modification import convert_input_to_dictionary, process_input, process_table, insert, read_textfile, set_by_path, execute_plugin
import pyH2A.Utilities.find_nearest as fn

def numpy_npv(rate, values):
	'''Calculation of net present value.
	'''

	values = np.asarray(values)
	return (values / (1+rate)**np.arange(0, len(values))).sum(axis=0)

@lru_cache(maxsize = None)
def get_idx(diagonal_number, axis0, axis1):
	'''Calculation of index for MACRS calculation.
	Uses ``lru_cache`` for repeated calculations.
	'''

	a = np.arange(0, diagonal_number)
	b = a[::-1]
	c = np.c_[a, b]

	idx = c[(c[:,0] <= axis0 - 1) & (c[:,1] <= axis1 - 1)]
	idx = (np.array(idx[:,0]), np.array(idx[:,1]))

	return idx

def MACRS_depreciation(plant_years, depreciation_length, annual_depreciable_capital):
	'''Calculation of MACRS depreciations.
	
	Parameters
	----------
	plant_years : ndarray
		Array of plant years.
	depreciation_length : int
		Depreciation length.
	annual_depreicable_capital : ndarray
		Depreciable capital by year.

	Returns 
	-------
	annual_charge : ndarray
		Charge by year.

	'''

	end_idx = len(plant_years)	

	original_macrs = read_textfile('pyH2A.Lookup_Tables~MACRS.csv', delimiter = '	')
	macrs = np.copy(original_macrs)

	macrs[1:,1:] = macrs[1:,1:]/100.
	idx_macrs = fn.find_nearest(macrs[0][1:], depreciation_length)[0] 
	macrs_values = macrs[1:,1:][:,idx_macrs]
	macrs_values = macrs_values[macrs_values != 0]

	depreciation = np.outer(annual_depreciable_capital, macrs_values)

	charge = []
	diagonals = sum(depreciation.shape) + 1

	for i in range(1, diagonals):
		idx = get_idx(i, depreciation.shape[0], depreciation.shape[1])

		diagonal = depreciation[idx]
		charge.append(np.sum(diagonal))

	charge = np.asarray(charge)

	annual_charge = charge[:end_idx]
	annual_charge[-1] += np.sum(charge[end_idx:])

	return annual_charge

def discounted_cash_flow_function(inp, values, parameters, attribute = 'h2_cost', 
											plugin = None, plugin_attr = None):
	'''Wrapper function for ``Discounted_Cash_Flow``, substituting provided values 
	at specified parameter positions and returning desired attribute of 
	``Discounted_Cash_Flow`` object.

	Parameters
	----------
	inp : dict or str
		Dictionary containing input information. If `inp` is a file path, the provided 
		file is converted to a dictionary using ``convert_input_to_dictionary``.
	values : ndarray
		1D (in case of one parameter) or 2D array (in case of multiple parameters)
		containing the values which are to be used.
	parameters : ndarray
		1D or 2D array containing the parameter specifications (location within inp);
		Format: [top_key, middle_key, bottom_key].
	attribute : str, optional
		Desired attribute of ``Discounted_Cash_Flow`` object, which should be returned.
		If the attribute is `plugs`, the `.plugs` dictionary attribute is accessed, which 
		contains information of all used plugins (see `plugin` and `plugin_attr`).
		Defaults to `h2_cost`.
	plugin : str, optional
		If `attribute` is set to `plugs`, a `plugin` has to be specified, which should be 
		accessed. Furthermore, a corresponding attribute of the plugin needs to be provided,
		see `plugin_attr`.
	plugin_attr : str, optional
		If `attribute` is set to `plugs`, `plugin_attr` controls which attribute of the 
		specified `plugin` is accessed.

	Returns
	-------
	results : ndarray
		For each value (1D array) or set of values (2D array), the values are 
		substituted in inp, Discounted_Cash_Flow (dcf) is executed and the dcf 
		object is generated. Then, the requested attribute is stored in results, 
		which is finally returned.
	'''

	if isinstance(inp, str):
		inp = convert_input_to_dictionary(inp)

	results = []

	for value_set in values:
		input_dict = copy.deepcopy(inp)

		if isinstance(value_set, numbers.Number):
			set_by_path(input_dict, parameters, value_set)

		else:
			for value, parameter in zip(value_set, parameters):
				set_by_path(input_dict, parameter, value)

		dcf = Discounted_Cash_Flow(input_dict, print_info = False)

		result = getattr(dcf, attribute)

		if attribute == 'plugs':
			result = result[plugin]
			result = getattr(result, plugin_attr)

		results.append(result)

	return results

class Discounted_Cash_Flow:
	'''Class to perform discounted cash flow analysis.

	Parameters
	----------
	Workflow > initial_equity_depreciable_capital > Type : function
		Initial equity depreciable capital function.
	Workflow > initial_equity_depreciable_capital > Position : int
		Position of initial equity depreciable capital function.
	Workflow > non_depreciable_capital_costs > Type : function
		Non-depreciable capital costs function.
	Workflow > non_depreciable_capital_costs > Position : int
		Position of non-depreciable capital costs function.
	Workflow > replacement_costs > Type : function
		Replacement costs function.
	Workflow > replacement_costs > Position : int
		Position of replacement costs function.	
	Workflow > fixed_operating_costs > Type : function
		Fixed operating costs function.
	Workflow > fixed_operating_costs > Position : int
		Position of fixed operating costs function.
	Workflow > variable_operating_costs > Type : function
		Variable operating costs function.
	Workflow > variable_operating_costs > Position : int
		Position of variable operating costs function.
	Workflow > [...] > Type : plugin, optional
		Plugin to be executed.
	Workflow > [...] > Position : int, optional
		Position of plugin to be executed.
	Technical Operating Parameters and Specifications > Output per Year at Gate > Value : float
		Output per year at gate in kg.
	Financial Input Values > ref year > Value : int
		Financial reference year.
	Financial Input Values > startup year > Value : int
		Startup year for plant.
	Financial Input Values > basis year > Value : int
		Financial basis year.
	Financial Input Values > current year capital costs > Value : int
		Current year for capital costs.
	Financial Input Values > startup time > Value : int
		Startup time in years. 
	Financial Input Values > plant life > Value : int
		Plant life in years.
	Financial Input Values > analysis period > Value : int
		Analysis period in years.
	Financial Input Values > depreciation length > Value : int
		Depreciation length in years.
	Financial Input Values > depreciation type > Value : str
		Type of depreciation, currently only MACRS is implemented.
	Financial Input Values > equity > Value : float
		Percentage of equity financing.
	Financial Input Values > interest > Value : float
		Interest rate on debt.
	Financial Input Values > debt > Value : str
		Debt period, currently only constant debt is implemented.
	Financial Input Values > startup cost fixed > Value : float
		Percentage of fixed operating costs during start-up.
	Financial Input Values > startup revenues > Value : float
		Percentage of revenues during start-up.
	Financial Input Values > startup cost variable > Value : float
		Percentage of variable operating costs during start-up.
	Financial Input Values > decommissioning > Value : float
		Decomissioning cost in percentage of depreciable capital investment.
	Financial Input Values > salvage > Value : float
		Salvage value in percentage of total capital investment.
	Financial Input Values > inflation > Value : float
		Inflation rate.
	Financial Input Values > irr > Value : float
		After tax real internal rate of return.
	Financial Input Values > state tax > Value : float
		State tax.
	Financial Input Values > federal tax > Value : float
		Federal tax.
	Financial Input Values > working capital > Value : float
		Working capital as percentage of yearly change in operating costs.
	Construction > [...] > Value : float
		Percentage of capital spent in given year of construction. Number of entries 
		determines construction period in year (each entry corresponds to one year).
		Have to be in order (first entry corresponds to first construction year etc.)
		Values of all entries have to sum to 100%.
	Depreciable Capital Costs > Inflated > Value : float
		Inflated depreciable capital costs.
	Non-Depreciable Capital Costs > Inflated > Value : float
		Inflated non-depreciable capital costs.
	Replacement > Total > Value : float
		Total replacement costs.
	Fixed Operating Costs > Total > Value : float
		Total fixed operating costs.
	Variable Operating Costs > Total > Value : float
		Total variable operating costs.

	Returns
	-------
	Discounted_Cash_Flow : object
		Discounted cash flow analysis object.

	Attributes
	----------
	h2_cost : float
		Levelized H2 cost per kg.
	contributions : dict
		Cost contributions to H2 price.
	plugs : dict 
		Dictionary containing plugin class objects used during analysis.

	Notes
	-----
	**Numerical inputs**

	Numbers use decimal points. Commas can be used as thousands seperator, they are removed from numbers
	during processing. the "%" can be used after a number, indicating that it will be divided by 100
	before being used. 

	**Special symbols**

	Tables in the input file are formatted using GitHub flavoured Markdown. 
	This means that "#" at the beginning of a line indicates a header.
	"|" is used to seperate columns.
	"---" is used on its own line to seperate table headers from table entries.

	Paths to locations in the input file/in self.inp are specified using ">". Paths are always composed
	of three levels: top key > middle key > bottom key.

	File name paths are specified using "/".

	In cases where multiple numbers are used in one field (e.g. during sensitivity analysis), these numbers
	are seperated using ";".

	**Order in the input file**

	Order matters in the following cases: 

	1. For a group of ``sum_all_tables()`` processed tables (sharing the specified part of their key, e.g. "Direct
	Capital Cost"), they are processed in their provided order.
	
	2. Within a table, the first column will be used to generate the "middle key" of self.inp. The order of the
	other columns is not important.

	**Input**

	Processed input cells can contain either a number or path(s) (if multiple paths are used, they have to
	be seperated by ";") to other cells. The use of process_input() (and hence, process_table(), sum_table() and 
	sum_all_tables()) also allows for the value of an input cell to be multiplied by another cell by including
	path(s) in an additiona column (column name typically "Path").

	**Workflow**

	Workflow specifies which functions and plugins are used and in which order they are executed. The listed
	five functions have to be executed in the specified order for pyH2A to work. Plugins can be inserted at 
	appropiate positions (Type: "plugin"). Plugins have to be located in the ./Plugins/ directory. Execcution
	order is determined by the "Position" input. If the specified position is equal to an already exisiting one,
	the function/plugin will be executed after the already specified one. If multiple plugins/function are
	specified with the same position, they will be executed in the order in which they are listed in the 
	input file.

	**Plugins**

	Plugins needs to be composed of a class with the same name as the plugin file name. This class uses two inputs, 
	a discounted cash flow object (usually indicated by "self") and "print_info", which controls the printing of run time
	statements. Within the __init__ function of the class the actions of the plugins are specified, typically call(s)
	of the "insert()" function to modify the discounted cash flow object's "inp" dictionary (self.inp).
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

		self.workflow(self.inp, self.npv_dict, self.plugs)  # execution of all functions and plugins specified in "Workflow"

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

	def workflow(self, inp, npv_dict, plugs_dict):
		'''Executing plugins and functions for discounted cash flow.
		'''

		sorted_keys = sorted(inp['Workflow'], key = lambda x: inp['Workflow'][x]['Position'])

		for key in sorted_keys:
			if inp['Workflow'][key]['Type'] == 'function':
				self.execute_function(key, npv_dict)
			else:
				execute_plugin(key, plugs_dict, print_info = self.print_info, dcf = self)
	
	def execute_function(self, function_name, npv_dict):
		'''Execute class function named `function_name` and store output in `npv_dict`'''

		called_function = getattr(self, function_name)
		output = called_function()
		npv_dict[function_name] = output

	def time(self):
		'''Creating time scale information for discounted cash flow analysis.
		'''

		insert(self, 'Financial Input Values', 'construction time', 'Value', 
			   len(self.inp['Construction']), __name__, print_info = self.print_info)

		construction_start = self.fin['startup year']['Value'] - self.fin['construction time']['Value']
		end_of_life = self.fin['startup year']['Value'] + self.fin['plant life']['Value']

		self.years = np.arange(construction_start, end_of_life)
		self.analysis_years = np.arange(0, self.fin['construction time']['Value'] + 
										   self.fin['plant life']['Value'])
		self.plant_years = np.arange(-self.fin['construction time']['Value'], 
									  self.fin['plant life']['Value'])
		self.operation_years = np.arange(0, self.fin['plant life']['Value'])

	def inflation(self):
		'''Calculate inflation correction and inflators for specific commodities.
		'''

		inflation_rate = 1 + self.fin['inflation']['Value']
		self.inflation_factor = inflation_rate ** self.plant_years
		self.inflation_correction = inflation_rate ** (self.fin['startup year']['Value'] - 
			      									   self.fin['ref year']['Value'])

		plant_cost = read_textfile('pyH2A.Lookup_Tables~Plant_Cost_Index.csv', 
			  						delimiter = '	')
		gdp_deflator_price = read_textfile('pyH2A.Lookup_Tables~GDP_Implicit_Deflator_Price_Index.csv', 
											delimiter = '	')
		labor_price = read_textfile('pyH2A.Lookup_Tables~Labor_Index.csv', 
									 delimiter = '	')
		chemical_price = read_textfile('pyH2A.Lookup_Tables~SRI_Chemical_Price_Index.csv', 
										delimiter = '	')

		plant_idx = fn.find_nearest(plant_cost, [self.fin['current year capital costs']['Value'], 
												 self.fin['basis year']['Value']])
		gdp_idx = fn.find_nearest(gdp_deflator_price, [self.fin['ref year']['Value'], 
													   self.fin['current year capital costs']['Value']])
		labor_idx = fn.find_nearest(labor_price, [self.fin['ref year']['Value'], 
												  self.fin['basis year']['Value']])
		chemical_idx = fn.find_nearest(chemical_price, [self.fin['ref year']['Value'], 
														self.fin['basis year']['Value']])

		self.cepci_inflator = plant_cost[:,1][plant_idx[0]]/plant_cost[:,1][plant_idx[1]]
		self.ci_inflator = gdp_deflator_price[:,1][gdp_idx[0]]/gdp_deflator_price[:,1][gdp_idx[1]]
		self.combined_inflator = self.cepci_inflator * self.ci_inflator
		self.labor_inflator = labor_price[:,1][labor_idx[0]]/labor_price[:,1][labor_idx[1]]
		self.chemical_inflator = chemical_price[:,1][chemical_idx[0]]/chemical_price[:,1][chemical_idx[1]]

	def production_scaling(self):
		'''Get plant outpuer per year at gate.
		'''

		self.output_per_year_at_gate = process_input(self.inp, 
										'Technical Operating Parameters and Specifications', 
										'Output per Year at Gate', 
										'Value')

		return 0.

	def initial_equity_depreciable_capital(self):
		'''Calculate initial equity depreciable capital.
		'''

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

		return numpy_npv(self.after_tax_nominal_irr, construction_years)

	def non_depreciable_capital_costs(self):
		'''Calculate non-depreciable capital costs.
		'''
		
		self.non_depreciable_capital = process_input(self.inp, 'Non-Depreciable Capital Costs', 'Inflated', 'Value')
		self.non_depreciable_capital_inflated = self.non_depreciable_capital * self.inflation_correction
		non_depreciable_capital_inflation_corrected = self.non_depreciable_capital_inflated * self.inflation_factor[0]

		self.annual_non_depreciable_capital = np.zeros(len(self.inflation_factor))
		self.annual_non_depreciable_capital[0] = non_depreciable_capital_inflation_corrected

		return non_depreciable_capital_inflation_corrected

	def replacement_costs(self):
		'''Calculate replacement costs.
		'''
	
		yearly_costs = self.inp['Replacement']['Total']['Value']

		self.start_idx = fn.find_nearest(self.plant_years, 0)[0]
		yearly_costs[:self.start_idx] = 0
		self.annual_replacement_costs = yearly_costs	

		return numpy_npv(self.after_tax_nominal_irr, yearly_costs)

	def salvage_decommissioning(self):
		'''Calculate salvage and decomissioning costs.
		'''

		self.total_capital_inflated = self.depreciable_capital_inflation + self.non_depreciable_capital_inflated

		decommissioning = self.depreciable_capital_inflation * self.fin['decommissioning']['Value']
		salvage = self.total_capital_inflated * self.fin['salvage']['Value']

		self.decommissioning_costs = np.zeros(len(self.plant_years))
		self.decommissioning_costs[-1] = decommissioning * self.inflation_factor[-1]

		self.salvage_income = np.zeros(len(self.plant_years))
		self.salvage_income[-1] = salvage * self.inflation_factor[-1]

		return numpy_npv(self.after_tax_nominal_irr, self.salvage_income), numpy_npv(self.after_tax_nominal_irr, self.decommissioning_costs)

	def fixed_operating_costs(self):
		'''Calculate fixed operating costs.
		'''

		fixed_operating = process_input(self.inp, 'Fixed Operating Costs', 'Total', 'Value')
		fixed_operating_inflated = fixed_operating * self.inflation_correction

		self.start_up_time_idx = self.start_idx + self.fin['startup time']['Value']

		yearly_costs = fixed_operating_inflated * self.inflation_factor
		yearly_costs[:self.start_up_time_idx] = yearly_costs[:self.start_up_time_idx] * self.fin['startup cost fixed']['Value']
		yearly_costs[:self.start_idx] = 0

		self.fixed_operating_costs = yearly_costs

		return numpy_npv(self.after_tax_nominal_irr, yearly_costs)

	def variable_operating_costs(self):
		'''Calculate variable operating costs.
		'''

		variable_operating_costs = self.inflation_factor * self.inp['Variable Operating Costs']['Total']['Value']
		variable_operating_costs[:self.start_up_time_idx] = variable_operating_costs[:self.start_up_time_idx] * self.fin['startup cost variable']['Value']
		variable_operating_costs[:self.start_idx] = 0

		self.variable_operating_costs = variable_operating_costs

		return numpy_npv(self.after_tax_nominal_irr, variable_operating_costs)

	def working_capital_reserve_calc(self):
		'''Calculate working capital reserve.
		'''

		sum_variable_fixed_operating_costs = self.variable_operating_costs + self.fixed_operating_costs

		self.working_capital_reserve = -self.fin['working capital']['Value'] * np.diff(sum_variable_fixed_operating_costs)
		self.working_capital_reserve[-1] = -np.sum(self.working_capital_reserve[:-1])
		self.working_capital_reserve = np.r_[np.zeros(1), self.working_capital_reserve]

		return -numpy_npv(self.after_tax_nominal_irr, self.working_capital_reserve)

	def debt_financing(self):
		'''Calculate constant debt financing.
		'''

		self.debt_financed_capital = self.depreciable_capital_inflation * (1 - self.fin['equity']['Value']) * self.inflation_factor[0]
		interest = self.debt_financed_capital * self.fin['interest']['Value']
		self.interest_per_year = np.ones(len(self.inflation_factor)) * interest

		self.principal_payment = np.zeros(len(self.inflation_factor))
		self.principal_payment[-1] = self.debt_financed_capital

		return numpy_npv(self.after_tax_nominal_irr, self.interest_per_year), numpy_npv(self.after_tax_nominal_irr, self.principal_payment)

	def depreciation_charge(self):
		'''Calculate depreciation charge.
		'''

		total_initial_depreciable_capital = self.debt_financed_capital + self.initial_depreciable_capital
		annual_depreciable_capital = np.copy(self.annual_replacement_costs)
		annual_depreciable_capital[self.start_idx] += total_initial_depreciable_capital

		self.annual_charge = MACRS_depreciation(self.plant_years, self.fin['depreciation length']['Value'], annual_depreciable_capital)		

		return numpy_npv(self.after_tax_nominal_irr, self.annual_charge)

	def h2_sales(self):
		'''Calculate H2 sales.
		'''

		self.annual_sales = np.ones(len(self.inflation_factor)) * self.output_per_year_at_gate
		self.annual_sales[:self.start_up_time_idx] = self.annual_sales[:self.start_up_time_idx] * self.fin['startup revenues']['Value']
		self.annual_sales[:self.start_idx] = 0

		return numpy_npv(self.fin['irr']['Value'], self.annual_sales)

	def h2_cost(self):
		'''Calculate levelized H2 cost.
		'''

		self.total_tax_rate = self.fin['federal tax']['Value'] + self.fin['state tax']['Value'] * (1. - self.fin['federal tax']['Value'])

		lcoe_capital_costs = self.npv_dict['initial_equity_depreciable_capital'] + self.npv_dict['non_depreciable_capital_costs'] + self.npv_dict['replacement_costs'] + self.npv_dict['working_capital_reserve']
		lcoe_depreciation = -self.npv_dict['depreciation_charge'] * self.total_tax_rate
		lcoe_principal_payment = self.npv_dict['principal_payment']
		lcoe_operating_costs = (-self.npv_dict['salvage'] + self.npv_dict['decomissioning'] + self.npv_dict['fixed_operating_costs'] + self.npv_dict['variable_operating_costs'] + self.npv_dict['interest']) * (1. - self.total_tax_rate)
		lcoe_h2_sales = self.npv_dict['h2_sales'] * (1. - self.total_tax_rate)

		self.h2_cost_nominal = (lcoe_capital_costs + lcoe_depreciation + lcoe_principal_payment + lcoe_operating_costs)/lcoe_h2_sales * (1. + self.fin['inflation']['Value']) ** self.fin['construction time']['Value']
		self.h2_cost = self.h2_cost_nominal/self.inflation_correction

	def h2_revenue(self):
		'''Calculate H2 sales revenue.
		'''

		self.annual_revenue = self.annual_sales * self.h2_cost_nominal * self.inflation_factor

		return numpy_npv(self.after_tax_nominal_irr, self.annual_revenue)

	def income(self):
		'''Calculate total income.
		'''

		self.annual_pre_depreciation_income = self.annual_revenue + self.salvage_income - self.decommissioning_costs - self.fixed_operating_costs - self.variable_operating_costs - self.interest_per_year
		self.taxable_income = self.annual_pre_depreciation_income - self.annual_charge
		self.annual_taxes = self.taxable_income * self.total_tax_rate
		self.after_tax_income = self.annual_pre_depreciation_income - self.annual_taxes

		return numpy_npv(self.after_tax_nominal_irr, self.annual_pre_depreciation_income), numpy_npv(self.after_tax_nominal_irr, self.taxable_income), numpy_npv(self.after_tax_nominal_irr, self.annual_taxes), numpy_npv(self.after_tax_nominal_irr, self.after_tax_income)

	def cash_flow(self):
		'''Calculate cash flow.
		'''

		pre_tax_cash_flow = -self.annual_initial_depreciable_capital - self.annual_replacement_costs + self.working_capital_reserve - self.annual_non_depreciable_capital + self.annual_pre_depreciation_income - self.principal_payment
		after_tax_post_depreciation_cash_flow = pre_tax_cash_flow - self.annual_taxes

		npv_after_tax_post_depreciation = numpy_npv(self.after_tax_nominal_irr, after_tax_post_depreciation_cash_flow)

		if abs(npv_after_tax_post_depreciation) > 1e-6:
			print('Warning: NPV of After tax post-depreciation cash flow is not 0, possible error. NPV: {0}'.format(npv_after_tax_post_depreciation))

		cummulative_cash_flow = np.cumsum(after_tax_post_depreciation_cash_flow)

		return numpy_npv(self.after_tax_nominal_irr, cummulative_cash_flow)

	def cost_contribution(self):
		'''Compile contributions to H2 cost.
		'''

		revenue = self.expenses_per_kg_H2(self.npv_dict['revenue'])

		self.contributions = {'Data': {'Initial equity depreciable capital': self.expenses_per_kg_H2(self.npv_dict['initial_equity_depreciable_capital']),
						   			   'Non depreciable capital' : self.expenses_per_kg_H2(self.npv_dict['non_depreciable_capital_costs']),
						 			   'Replacement costs' : self.expenses_per_kg_H2(self.npv_dict['replacement_costs']),
						      		   'Salvage' : -self.expenses_per_kg_H2(self.npv_dict['salvage']),
						 	  		   'Decomissioning' : self.expenses_per_kg_H2(self.npv_dict['decomissioning']),
						  	  		   'Fixed operating costs' : self.expenses_per_kg_H2(self.npv_dict['fixed_operating_costs']),
						 	  		   'Variable operating costs' : self.expenses_per_kg_H2(self.npv_dict['variable_operating_costs']),
						 	  		   'Working capital reserve' : self.expenses_per_kg_H2(self.npv_dict['working_capital_reserve']),
						   	  		   'Interest' : self.expenses_per_kg_H2(self.npv_dict['interest']),
						      		   'Principal payment' : self.expenses_per_kg_H2(self.npv_dict['principal_payment']),
						      		   'Taxes' : self.expenses_per_kg_H2(self.npv_dict['taxes'])}
						      		   }

		self.contributions['Total'] = self.h2_cost
		self.contributions['Table Group'] = 'Total cost of hydrogen'

	def expenses_per_kg_H2(self, value):
		'''Calculate expenses per kg H2.
		'''

		return value/self.npv_dict['h2_sales'] * (1. + self.fin['inflation']['Value']) ** self.fin['construction time']['Value'] / self.inflation_correction

	def check_processing(self):
		'''Check whether all tables in input file were used.

		Notes
		-----
		'Workflow' and 'Display Parameters' tables are exempted.
		Furthermore, all tables that have the term 'Analysis' in their name
		are also exempted.

		'''

		exceptions = ['Workflow', 'Display Parameters']

		for top_key in self.inp:
			if top_key not in exceptions and 'Analysis' not in top_key:
				for middle_key in self.inp[top_key]:
					if 'Processed' not in self.inp[top_key][middle_key]:
						print('Warning: "{0} > {1}" has not been processed'.format(top_key, middle_key))

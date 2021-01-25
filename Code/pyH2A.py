import numpy as np
import copy
import sys
from fpdf import FPDF
import find_nearest as fn
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12

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

			if line == '\n':
				table = False
				header = True

			if line[0] == '-':
				table = True
				header = False

			if header is True and line != '\n':
				header_entries = line.split('|')

			if table is True and line[0] != '-':
				table_entries = line.split('|')
				inp[variable_name][table_entries[0].strip(' ')] = {}

				for i in zip(header_entries[1:], table_entries[1:]):
					header_entry = i[0].strip(' \n')
					table_entry = num(i[1].strip(' \n'))
					inp[variable_name][table_entries[0].strip(' ')][header_entry] = table_entry 

	return inp

def parse_parameter(key, delimiter = '>'):

	path_components = key.split(delimiter)
	output = []

	for i in path_components:
		output.append(i.strip(' '))
		
	return output	

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

	def __init__(self, input_file, print_info = True):
		if isinstance(input_file, str):
			self.inp = convert_input_to_dictionary(input_file)
		else:
			self.inp = input_file

		self.check_plugins()

		self.fin = self.inp['Financial Input Values']
		self.time()
		self.inflation()
		self.production_scaling()

		if 'Photocatalytic_Plugin' in self.plugins:
			from Photocatalytic_Plugin import Photocatalytic_Plugin
			Photocatalytic_Plugin(self, print_info)

		if 'Multiple_Modules_Plugin' in self.plugins:
			from Multiple_Modules_Plugin import Multiple_Modules_Plugin
			Multiple_Modules_Plugin(self, print_info)

		self.npv_initial_equity_depreciable_capital = self.initial_equity_depreciable_capital()
		self.npv_non_depreciable_capital_costs = self.non_depreciable_capital_costs()
		self.npv_replacement_costs = self.replacement_costs()
		self.npv_salvage, self.npv_decomissioning = self.salvage_decommissioning()
		self.npv_fixed_operating_costs = self.fixed_operating_costs()
		self.electricity_cost_per_kg = self.industrial_electricity()
		self.water_cost_per_kg = self.process_water()
		self.npv_variable_operating_costs = self.variable_operating_costs()
		self.npv_working_capital_reserve = self.working_capital_reserve_calc()
		self.npv_interest, self.npv_principal_payment = self.debt_financing()
		self.npv_depreciation_charge = self.depreciation_charge()
		self.npv_h2_sales = self.h2_sales()
		self.h2_cost()
		self.npv_revenue = self.h2_revenue()
		self.npv_pre_depreciation_income, self.npv_taxable_income, self.npv_taxes, self.npv_after_tax_income = self.income()
		self.cash_flow()
		self.cost_contribution()

	def check_plugins(self):

		try:
			self.plugins = self.inp['Plugins']['Plugins']['Value']	
			self.plugins = parse_parameter(self.plugins, delimiter = ';')
		except KeyError:
			self.plugins = []

	def time(self):

		self.fin['construction time'] = {'Full Name': 'Length of Construction Period (years)', 'Value': len(self.inp['Construction'])}

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

		plant_idx = fn.find_nearest(plant_cost, [self.fin['current year capital costs']['Value'], self.fin['basis year']['Value']])
		gdp_idx = fn.find_nearest(gdp_deflator_price, [self.fin['ref year']['Value'], self.fin['current year capital costs']['Value']])
		labor_idx = fn.find_nearest(labor_price, [self.fin['ref year']['Value'], self.fin['basis year']['Value']])

		self.cepci_inflator = plant_cost[:,1][plant_idx[0]]/plant_cost[:,1][plant_idx[1]]
		self.ci_inflator = gdp_deflator_price[:,1][gdp_idx[0]]/gdp_deflator_price[:,1][gdp_idx[1]]
		self.combined_inflator = self.cepci_inflator * self.ci_inflator
		self.labor_inflator = labor_price[:,1][labor_idx[0]]/labor_price[:,1][labor_idx[1]]

	def production_scaling(self):

		operating = self.inp['Technical Operating Parameters and Specifications']

		self.max_output_per_day = operating['Plant Design Capacity (kg of H2/day)']['Value'] * operating['Scaling Ratio']['Value']
		self.output_per_year = operating['Operating Capacity Factor (%)']['Value'] * self.max_output_per_day * 365.

		self.capital_scaling_factor = operating['Scaling Ratio']['Value'] ** operating['Scaling Exponent']['Value']
		self.labor_scaling_factor = operating['Scaling Ratio']['Value'] ** 0.25

	def initial_equity_depreciable_capital(self):

		direct_scaling = self.inp['Total Capital Costs']['Scaling Direct Capital Cost']['Value'] * self.capital_scaling_factor * self.combined_inflator
		direct_non_scaling = self.inp['Total Capital Costs']['Non-Scaling Direct Capital Cost']['Value'] * self.combined_inflator

		indirect = 0.
		for key in self.inp['Indirect Depreciable Capital Costs']:
			indirect += self.inp['Indirect Depreciable Capital Costs'][key]['Value'] * self.combined_inflator * self.capital_scaling_factor

		self.depreciable_capital = direct_scaling + direct_non_scaling + indirect
		self.depreciable_capital_inflation = self.depreciable_capital * self.inflation_correction

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

		self.non_depreciable_capital = self.inp['Non-Depreciable Capital Costs']['Cost of land ($ per acre)']['Value'] * self.inp['Non-Depreciable Capital Costs']['Land required (acres)']['Value']
		self.non_depreciable_capital += self.inp['Non-Depreciable Capital Costs']['Other non-depreciable capital costs ($)']['Value']
		self.non_depreciable_capital *= self.ci_inflator

		self.non_depreciable_capital_inflated = self.non_depreciable_capital * self.inflation_correction
		non_depreciable_capital_inflation_corrected = self.non_depreciable_capital_inflated * self.inflation_factor[0]

		self.annual_non_depreciable_capital = np.zeros(len(self.inflation_factor))
		self.annual_non_depreciable_capital[0] = non_depreciable_capital_inflation_corrected

		return non_depreciable_capital_inflation_corrected

	def replacement_costs(self):
		'''Replacement costs are billed annually, replacements which are performed at a non-integer rate are corrected using non_interger_correction'''

		unplanned_replacement_cost = self.inp['Unplanned Replacement']['unplanned replacement']['Value'] * self.depreciable_capital
		unplanned_replacement_cost_inflated = unplanned_replacement_cost * self.inflation_correction

		yearly_costs = self.inflation_factor * unplanned_replacement_cost_inflated

		for key in self.inp['Planned Replacement']:
			defined_frequency = self.inp['Planned Replacement'][key]['Frequency (years)']
			replacement_frequency = int(np.ceil(defined_frequency))
			non_integer_correction = replacement_frequency / defined_frequency

			replacement_cost = self.inp['Planned Replacement'][key]['Cost ($)'] * non_integer_correction * self.combined_inflator
			replacement_cost_inflated = replacement_cost * self.inflation_correction

			initial_replacement_year_idx = fn.find_nearest(self.plant_years, replacement_frequency)[0]

			replacement_years = self.plant_years[initial_replacement_year_idx:][0::replacement_frequency]
			replacement_years_idx = fn.find_nearest(self.plant_years, replacement_years)

			yearly_costs[replacement_years_idx] += replacement_cost_inflated * self.inflation_factor[replacement_years_idx]

		self.start_idx = fn.find_nearest(self.plant_years, 0)[0]
		yearly_costs[:self.start_idx] = 0
		self.annual_replacement_costs = yearly_costs	

		return np.npv(self.after_tax_nominal_irr, yearly_costs)
		#return 5789124.0

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

		fix = self.inp['Fixed Operating Costs']

		labor_cost = fix['staff']['Value'] * fix['labor cost']['Value'] * 2080. * self.labor_inflator * self.labor_scaling_factor
		
		g_and_a = fix['g&a']['Value'] * labor_cost

		self.total_capital = self.depreciable_capital + self.non_depreciable_capital
		tax_insurance = fix['property tax']['Value'] * self.total_capital

		fixed_operating = labor_cost + g_and_a + tax_insurance

		for key in self.inp['Other Fixed Operating Costs']:
			fixed_operating += self.inp['Other Fixed Operating Costs'][key]['Value'] * self.combined_inflator

		fixed_operating_inflated = fixed_operating * self.inflation_correction

		self.start_up_time_idx = self.start_idx + self.fin['startup time']['Value']

		yearly_costs = fixed_operating_inflated * self.inflation_factor
		yearly_costs[:self.start_up_time_idx] = yearly_costs[:self.start_up_time_idx] * self.fin['startup cost fixed']['Value']
		yearly_costs[:self.start_idx] = 0

		self.fixed_operating_costs = yearly_costs

		return np.npv(self.after_tax_nominal_irr, yearly_costs)

	def industrial_electricity(self):

		electricity = self.inp['Energy Feedstocks, Utilities, and Byproducts']['Industrial Electricity']

		prices = np.genfromtxt('../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv', delimiter = '	') # Fixed Reference Case
		years_idx = fn.find_nearest(prices, self.years)
		prices = prices[years_idx]

		cost_per_kg_H2 = prices[:,1] * self.inflation_correction * electricity['Price Conversion Factor (GJ/kWh)'] * electricity['Usage (kWh/kg H2)']
		
		return cost_per_kg_H2

	def process_water(self):

		water = self.inp['Materials and Byproducts']['Process Water']
		annual_cost_per_kg_H2 = self.inflation_correction * water['$(2016)/gal'] * water['Usage per kg H2']

		cost_per_kg_H2 = np.ones(len(self.inflation_factor)) * annual_cost_per_kg_H2

		return cost_per_kg_H2

	def variable_operating_costs(self):

		other_variable_operating_costs = 0.
		for key in self.inp['Other Variable Operating Costs']:
			other_variable_operating_costs += self.inp['Other Variable Operating Costs'][key]['Value']

		utilities = self.output_per_year * (self.electricity_cost_per_kg + self.water_cost_per_kg)
		variable_operating_costs = self.inflation_factor * (utilities + other_variable_operating_costs)

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

		self.annual_sales = np.ones(len(self.inflation_factor)) * self.output_per_year
		self.annual_sales[:self.start_up_time_idx] = self.annual_sales[:self.start_up_time_idx] * self.fin['startup revenues']['Value']
		self.annual_sales[:self.start_idx] = 0

		return np.npv(self.fin['irr']['Value'], self.annual_sales)

	def h2_cost(self):

		self.total_tax_rate = self.fin['federal tax']['Value'] + self.fin['state tax']['Value'] * (1. - self.fin['federal tax']['Value'])

		lcoe_capital_costs = self.npv_initial_equity_depreciable_capital + self.npv_non_depreciable_capital_costs + self.npv_working_capital_reserve + self.npv_replacement_costs
		lcoe_depreciation = -self.npv_depreciation_charge * self.total_tax_rate
		lcoe_principal_payment = self.npv_principal_payment
		lcoe_operating_costs = (-self.npv_salvage + self.npv_decomissioning + self.npv_fixed_operating_costs + self.npv_variable_operating_costs + self.npv_interest) * (1. - self.total_tax_rate)
		lcoe_h2_sales = self.npv_h2_sales * (1. - self.total_tax_rate)

		# print(lcoe_capital_costs)
		# print(lcoe_depreciation)
		# print(lcoe_principal_payment)
		# print(lcoe_operating_costs)
		# print(lcoe_h2_sales)

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

		revenue = self.expenses_per_kg_H2(self.npv_revenue)

		self.contributions = {'Initial equity depreciable capital': self.expenses_per_kg_H2(self.npv_initial_equity_depreciable_capital),
						      'Non-depreciable capital' : self.expenses_per_kg_H2(self.npv_non_depreciable_capital_costs),
						 	  'Replacement costs' : self.expenses_per_kg_H2(self.npv_replacement_costs),
						      'Salvage' : -self.expenses_per_kg_H2(self.npv_salvage),
						 	  'Decomissioning' : self.expenses_per_kg_H2(self.npv_decomissioning),
						  	  'Fixed operating costs' : self.expenses_per_kg_H2(self.npv_fixed_operating_costs),
						 	  'Variable operating costs' : self.expenses_per_kg_H2(self.npv_variable_operating_costs),
						 	  'Working capital reserve' : self.expenses_per_kg_H2(self.npv_working_capital_reserve),
						   	  'Interest' : self.expenses_per_kg_H2(self.npv_interest),
						      'Principal payment' : self.expenses_per_kg_H2(self.npv_principal_payment),
						      'Taxes' : self.expenses_per_kg_H2(self.npv_taxes)}

	def expenses_per_kg_H2(self, value):

		return value/self.npv_h2_sales * (1. + self.fin['inflation']['Value']) ** self.fin['construction time']['Value'] / self.inflation_correction

class Sensitivity_Analysis:

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

	def __init__(self, input_file, output_directory):
		self.input_file = input_file
		self.file_name = parse_file_name(self.input_file)
		self.output_directory = output_directory

		self.base_case = Discounted_Cash_Flow(self.input_file)

		cost_breakdown_figure = Figure(self.cost_breakdown, self.output_directory)
		cost_breakdown_figure.save()

		try:
			sensitivity_figure = Figure(self.sensitivity_box_plot, self.output_directory)
			sensitivity_figure.save()
		except KeyError:
			print('KeyError, sensitivity analysis not performed.')
			pass

		self.report()

	def cost_breakdown(self, label_offset = 0.5):

		sorted_keys = sorted(self.base_case.contributions, key = self.base_case.contributions.get)
		sorted_contributions = {}

		for key in sorted_keys:
			sorted_contributions[key] = self.base_case.contributions[key]

		fig, ax = plt.subplots()
		fig.subplots_adjust(left = 0.4)
		ax.set_xlabel(r'Levelized cost / USD per kg $H_{2}$')
		ax.grid(color = 'grey', linestyle = '--', linewidth = 0.2)
		cmap = plt.get_cmap('plasma')

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

	# dcf = Discounted_Cash_Flow('../Input/Future_PEC_Type_1.md')
	# print(dcf.h2_cost)

	# sensitivity = Sensitivity_Analysis('../Input/Future_PEC_Type_2.md')
	# print(sensitivity.results)

	# output = Output('../Input/Future_PEC_Type_2.md', '../Output/Future_PEC_Type_2/')
	# print(output.base_case.h2_cost)

	#plt.show()

	run_pyH2A()

if __name__ == '__main__':
	main()
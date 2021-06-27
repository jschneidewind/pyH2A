import sys
from Discounted_Cash_Flow import Discounted_Cash_Flow, discounted_cash_flow_function
from PDF_Report import report
from input_modification import parse_file_name, convert_input_to_dictionary, execute_plugin, parse_parameter, parse_parameter_to_list
from output_utilities import Figure
from timeit import default_timer as timer
import pprint as pp
import numpy as np # temporary
import copy  # temporary
import matplotlib.pyplot as plt # temporary
from functools import lru_cache # temporary

class pyH2A:

	def __init__(self, input_file, output_directory, print_info = False, generate_report = True):

		self.input_file = input_file
		self.output_directory = output_directory
		self.file_name = parse_file_name(self.input_file)
		self.inp = convert_input_to_dictionary(self.input_file)
		self.base_case = Discounted_Cash_Flow(self.input_file, print_info = print_info)

		self.meta_modules = {}
		self.meta_workflow()

		# if generate_report is True:
		# 	report(self.base_case, self.output_directory, self.file_name, sensitivity_performed, waterfall_performed)

	def meta_workflow(self):
		'''Naming convention for analysis module: in self.inp, the table title has to contain "Analysis" and the
		last part of the string (seperated by spaces) has to be the module name'''

		for key in self.inp:

			if 'Analysis' in key and 'Parameters' not in key and 'Methods' not in key:
				module_name = key.split(' ')[-1]

				self.execute_meta_module(module_name, self.meta_modules)

	def execute_meta_module(self, module_name, meta_dict):
		
		figure_indicators = ['plot', 'figure', 'chart']

		module = execute_plugin(module_name, meta_dict, plugin_module = False, nested_dictionary = True, input_file = self.input_file)

		for key in self.inp:

			if module_name in key and 'Methods' in key: 

				for row_name, table in self.inp[key].items():
					method_name = table['Method Name']
					method = getattr(module, method_name)

					arguments = parse_parameter(table['Arguments'], delimiter =';')
					values = parse_parameter_to_list(table['Values'], delimiter = ';')
					arguments = dict(zip(arguments, values))

					if any(indicator in method_name for indicator in figure_indicators):
						arguments['directory'] = self.output_directory
						try:
							meta_dict[module_name][row_name] = method(**arguments)
						except TypeError:
							meta_dict[module_name][row_name] = method(**arguments['directory'])
					else:
						try:
							meta_dict[module_name][row_name] = method(**arguments)
						except TypeError:
							meta_dict[module_name][row_name] = method()

def run_pyH2A():

	path_to_input = sys.argv[1]
	path_to_output = sys.argv[2] 

	output = pyH2A(path_to_input, path_to_output)

def main():

	# pec_type_1 = pyH2A('../Input/210613_Future_PEC_Type_1_Limit.md', '../Output/210627_Future_PEC_Type_1_Limit/')
	# print(pec_type_1.base_case.h2_cost)

	pv_e = pyH2A('../Input/210613_PV_E.md', '../Output/210627_PV_E/', print_info = False)
	print(pv_e.base_case.h2_cost)
	#pp.pprint(pv_e.base_case.inp['Fixed Operating Costs'])

	# pv_e = pyH2A('../Input/210511_Future_PEC_Type_4.md', '../Output/210613_Future_PEC_Type_4/', print_info = False)
	# print(pv_e.base_case.h2_cost)


	# inp = convert_input_to_dictionary('../Input/210512_Future_PEC_Type_1.md')

	# start = timer()

	# inp_dict = copy.deepcopy(inp)

	# dcf = Discounted_Cash_Flow(inp_dict, print_info = False)

	# end = timer()

	# print('H2 Cost:', dcf.h2_cost, '	Time:', end - start)
	# pp.pprint(dcf.inp['Catalyst']['Properties'])






	#pp.pprint(dcf.plugs['Capital_Cost_Plugin'].direct_contributions)

	#pp.pprint(vars(dcf.plugs['Photocatalytic_Plugin']))

	#pp.pprint(dcf.inp['Solar Input'])


	# print('Mean Irradiation:', np.sum(dcf.plugs['Hourly_Irradiation_Plugin'].power_kW)/365.)


	# oversize_ratios = np.linspace(1., 2., 100)

	# results = discounted_cash_flow_function('../Input/210509_PV_E_Stolten.md', oversize_ratios, 
	# 										['Photovoltaic', 'Nominal Power (kW)', 'Value'])

	# plt.plot(oversize_ratios, results)
	# plt.show()




	# azimuth_angles = np.linspace(0, 360, 100)

	# results = discounted_cash_flow_function('../Input/210509_PV_E_Stolten.md', azimuth_angles, 
	# 							['Photovoltaic - Irradiance Parameters', 'Array Azimuth (degrees)', 'Value'],
	# 							attribute = 'plugs', plugin = 'Hourly_Irradiation_Plugin', plugin_attr = 'power_kW')

	# results = np.sum(np.asarray(results), axis = 1)/365.

	# plt.plot(azimuth_angles, results, '.')
	# plt.show()

	# start = timer()

	# inp_dict = copy.deepcopy(inp)



	# dcf = Discounted_Cash_Flow(inp_dict, print_info = False)
	
	# end = timer()
	# print(dcf.h2_cost, end - start)






	# start = timer()

	# dcf = Discounted_Cash_Flow('../Input/210416_PV_E_Chang.md', print_info = False)
	
	# end = timer()
	# print(dcf.h2_cost, end - start)

	# input_dict = convert_input_to_dictionary('../Input/Future_PEC_Type_1.md')
	# sth_values = np.linspace(0.01, 0.2, 20)

	# results = []


	# start = timer()

	# for sth in sth_values:
	# 	inp_dict = copy.deepcopy(input_dict)
	# 	inp_dict['Solar-to-Hydrogen Efficiency']['STH (%)']['Value'] = sth

	# 	dcf = Discounted_Cash_Flow(inp_dict, print_info = False)

	# 	results.append(dcf.h2_cost)
	


	# end = timer()

	# print(end - start)


	# plt.plot(sth_values, results, 'o-')
	# plt.show()





	# output = pyH2A('../Input/210509_PV_E_Stolten.md', '../Output/210510_PV_E_Stolten/', 
	# 			   cost_contributions = True, waterfall_analysis = True, sensitivity_analysis = True, generate_report = True)
	# print(output.base_case.h2_cost)


def secondary():

	input_dict = convert_input_to_dictionary('../Input/210416_PV_E_Chang.md')
	pv_powers = np.linspace(1.3, 2.0, 50)

	results = []

	for power in pv_powers:
		inp_dict = copy.deepcopy(input_dict)
		inp_dict['Photovoltaic']['Nominal Power (kW)']['Value'] = power
		dcf = Discounted_Cash_Flow(inp_dict, print_info = False)

		results.append(dcf.h2_cost)

	plt.plot(pv_powers, results)
	plt.show()

def tertiary():

	dcf = Discounted_Cash_Flow('../Input/Future_PEC_Type_1.md', print_info = False)
	print(dcf.h2_cost)

	pp.pprint(dcf.plugs['Capital_Cost_Plugin'].direct_contributions)

	pp.pprint(dcf.contributions)

	cost_contributions = Cost_Contributions(dcf.contributions)
	cost_contributions = Cost_Contributions(dcf.lugs['Capital_Cost_Plugin'].direct_contributions)

	cost_contributions_figure = Figure(cost_contributions.cost_breakdown, '../Output/210409_Future_PEC_Type_1/')
	cost_contributions_figure.show()


if __name__ == '__main__':
	run_pyH2A()
	#main()
	#run_pyH2A()

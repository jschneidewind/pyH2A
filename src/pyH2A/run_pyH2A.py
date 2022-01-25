import sys
import ast
import os
from pyH2A.Discounted_Cash_Flow import Discounted_Cash_Flow
from pyH2A.Utilities.input_modification import convert_input_to_dictionary, execute_plugin, convert_dict_to_kwargs_dict, check_for_meta_module

from timeit import default_timer as timer

import pprint

class pyH2A:
	'''pyH2A class that performs discounted cash flow analysis and executes analysis modules.

	Parameters
	----------
	input_file : str
		Path to input file.
	output_directory : str
		Path to output file.
	print_info : bool, optional
		Flag to control if detailed information during run of pyH2A is printed.

	Returns
	-------
	pyH2A : object
		pyH2A class object.

	Attributes
	----------
	inp : dict
		Dictionary containing input information and all information from discounted
		cash flow analysis.
	base_case : Discounted_Cash_Flow object
		Discounted_Cash_Flow object for base case defined in input file with corresponding
		attributes.
	meta_modules : dict
		Dictionary containing class instances of executes analysis modules.
	'''

	def __init__(self, input_file, output_directory, print_info = False):

		self.input_file = input_file
		self.file_name = os.path.basename(input_file).split('.')[0]
		self.output_directory = output_directory
		self.inp = convert_input_to_dictionary(self.input_file)
		self.base_case = Discounted_Cash_Flow(self.input_file, print_info = print_info)

		self.meta_modules = {}
		self.meta_workflow(self.meta_modules)

		print(f'Levelized cost of hydrogen (base case): {self.base_case.h2_cost} $/kg')

	def meta_workflow(self, meta_dict):
		'''Meta modules (analysis modules) are identified and executed

		Notes
		-----
		Naming convention for analysis module: in self.inp, the table title has to contain 
		`Analysis` and the last part of the string (seperated by spaces) has to be the module name'''

		for key in self.inp:
			if check_for_meta_module(key) is True:
				module_name = key.split(' ')[-1]
				self.execute_meta_module(module_name, meta_dict)

	def execute_meta_module(self, module_name, meta_dict):
		'''Requested module class is executed.
		'''
		
		module = execute_plugin(module_name, meta_dict, 
								plugin_module = False, 
								nested_dictionary = True, 
								input_file = self.input_file)

		for key in self.inp:
			if module_name in key and 'Methods' in key: 
				self.execute_module_methods(module, key, module_name, meta_dict)

	def execute_module_methods(self, module, key, module_name, meta_dict):
		'''Requested methods of module class are executed.
		'''

		for row_name, table in self.inp[key].items():
			method_name = table['Method Name']
			method = getattr(module, method_name)

			arguments = self.get_arguments(table)

			if self.check_for_plotting_method(method_name) is True:
				arguments['directory'] = self.output_directory
				arguments['input_file_name'] = self.file_name

			meta_dict[module_name][row_name] = method(**arguments)

	def get_arguments(self, table):
		'''Arguments are read from the table in self.inp referenced in
		table['Arguments'] or directly read from table['Arguments']
		'''

		try:
			arguments = table['Arguments']
		except KeyError:

			return {}

		try:
			return(convert_dict_to_kwargs_dict(self.inp[arguments]))
		except KeyError:
			return(ast.literal_eval(arguments))

	def check_for_plotting_method(self, method_name):
		'''Returns true if a plotting indicator substring is in
		`method_name`.
		'''

		plotting_indicators = ['plot', 'figure', 'chart']

		if any(indicator in method_name for indicator in plotting_indicators):
			return True
		else:
			return False

def run_pyH2A():
	'''Wrapper function to run pyH2A from the command line.
	'''

	path_to_input = sys.argv[1]
	path_to_output = sys.argv[2] 

	output = pyH2A(path_to_input, path_to_output)

	return output

def command_line_pyH2A(input_file, output_dir):
	'''Wrapper function to run pyH2A using click.
	'''

	output = pyH2A(input_file, output_dir)

	return output


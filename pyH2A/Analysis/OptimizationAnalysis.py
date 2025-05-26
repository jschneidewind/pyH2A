import numpy as np
from scipy.optimize import minimize, dual_annealing, differential_evolution, shgo
import matplotlib.pyplot as plt

from timeit import default_timer as timer

import pyH2A.Utilities.find_nearest as fn
from pyH2A.Utilities.input_modification import convert_input_to_dictionary,parse_parameter, parse_parameter_to_array, get_by_path, set_by_path, read_textfile, file_import, reverse_parameter_to_string
from pyH2A.DiscountedCashFlow import DiscountedCashFlow, DiscountedCashFlow_function, DiscountedCashFlow_function_1D
from pyH2A.Utilities.output_utilities import make_bold, format_scientific, dynamic_value_formatting, insert_image, Figure_Lean

class OptimizationAnalysis:
	'''Optimization of pyH2A models.

	Parameters
	----------


	'''

	def __init__(self, input_file):
		'''
		'''

		self.inp = convert_input_to_dictionary(input_file)

		# start = timer()

		# DiscountedCashFlow(self.inp, print_info = False)

		# end = timer()
		# print(end - start)

		self.process_parameters()
		self.perform_optimization()


	def process_parameters(self):
		'''Processing of parameters that are to be optimized. Parsing of parameter path and
		bounds (seperated by `;`).
		'''

		parameters = self.inp['Parameters - OptimizationAnalysis']

		self.parameters = []
		self.bounds = []

		for counter, key in enumerate(parameters):

			parameter = parse_parameter(key)
			bounds = parse_parameter_to_array(parameters[key]['Bounds'], delimiter = ';', 
											  dictionary = self.inp, 
											  top_key = 'Parameters - OptimizationAnalysis', 
											  middle_key = key, bottom_key = 'Bounds', 
											  special_values = ['Base', 'Reference'], 
											  path = key)

			self.parameters.append(parameter)
			self.bounds.append(bounds)

		self.bounds = np.asarray(self.bounds)
		self.bounds = np.sort(self.bounds, axis = 1)

	def perform_optimization(self):
		'''Performing optimization using differential evolution algorithm and 
		printing results.
		'''

		p = differential_evolution(func = DiscountedCashFlow_function_1D, 
								   bounds = self.bounds,
								   args = (self.parameters, self.inp))

		"""print('Optimization results:')
		print('--------------------------------------------------------------------------------')
		print(p)
		print('--------------------------------------------------------------------------------')

		for counter, parameter in enumerate(self.parameters):
			print(f'{parameter[0]} > {parameter[1]} > {parameter[2]}	 optimal value is {p.x[counter]}')

		print(f'Optimal levelized cost of hydrogen: {p.fun} $/kg')
		print('--------------------------------------------------------------------------------')"""
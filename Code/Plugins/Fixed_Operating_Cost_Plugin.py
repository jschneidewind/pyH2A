from input_modification import insert, sum_all_tables, process_table

class Fixed_Operating_Cost_Plugin:
	'''
	______________
	Required Input
	______________

	# Fixed Operating Costs
	Name | Value
	--- | ---
	staff | num
	hourly labor cost | num

	process_table() is used

	# Other Fixed Operating Cost [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	______________
	Output
	______________

	Insertion of "Summed Total" for each sum_all_tables() processed table

	Fixed Operating Costs > Labor Cost > Value
	Fixed Operating Costs > Total > Value
	'''


	def __init__(fixed, self, print_info):
		fixed.labor_cost(self)
		insert(self, 'Fixed Operating Costs', 'Labor Cost - Uninflated', 'Value', fixed.labor_uninflated, __name__, print_info = print_info)
		insert(self, 'Fixed Operating Costs', 'Labor Cost', 'Value', fixed.labor, __name__, print_info = print_info)

		fixed.other_cost(self, print_info)
		insert(self, 'Fixed Operating Costs', 'Total', 'Value', fixed.labor + fixed.other, __name__, print_info = print_info)

	def labor_cost(fixed, self):
		process_table(self.inp, 'Fixed Operating Costs', 'Value')

		fixed.labor_uninflated = self.inp['Fixed Operating Costs']['staff']['Value'] * self.inp['Fixed Operating Costs']['hourly labor cost']['Value'] * 2080.
		fixed.labor = fixed.labor_uninflated * self.labor_inflator 
	
	def other_cost(fixed, self, print_info):

		fixed.other = sum_all_tables(self.inp, 'Other Fixed Operating Cost', 'Value', insert_total = True, class_object = self, print_info = print_info) * self.combined_inflator


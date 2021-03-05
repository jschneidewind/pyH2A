from input_modification import insert, sum_all_tables, process_table
import pprint

class Capital_Cost_Plugin:
	'''
	______________
	Required Input
	______________

	# Direct Capital Cost [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	# Indirect Capital Costs [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	# Non-Depreciable Capital Costs
	Name | Value
	--- | ---
	Cost of land ($ per acre) | num
	Land required (acres) | num

	process_table() is used

	# Other Non-Depreciable Capital Cost [...]
	Name | Value
	--- | ---
	str | num

	sum_all_tables() processed

	______________
	Output
	______________

	Insertion of "Summed Total" for each sum_all_tables() processed table

	Direct Capital Costs > Total > Value
	Direct Capital Costs > Inflated > Value
	Indirect Capital Costs > Total > Value
	Indirect Capital Costs > Inflated > Value
	Non-Depreciable Capital Costs > Total > Value
	Non-Depreciable Capital Costs > Inflated > Value
	Depreciable Capital Costs > Total > Value
	Depreciable Capital Costs > Inflated > Value
	Total Capital Costs > Total > Value
	Total Capital Costs > Inflated > Value

	'''

	def __init__(capital, self, print_info):

		capital.direct_capital_costs(self, print_info)

		direct_inflated = capital.direct * self.combined_inflator

		insert(self, 'Direct Capital Costs', 'Total', 'Value', capital.direct, __name__, print_info = print_info)
		insert(self, 'Direct Capital Costs', 'Inflated', 'Value', direct_inflated, __name__, print_info = print_info)

		capital.indirect_capital_costs(self, print_info)

		indirect_inflated = capital.indirect * self.combined_inflator
		depreciable = capital.direct + capital.indirect
		depreciable_inflated = direct_inflated + indirect_inflated
		
		insert(self, 'Indirect Capital Costs', 'Total', 'Value', capital.indirect, __name__, print_info = print_info)
		insert(self, 'Indirect Capital Costs', 'Inflated', 'Value', indirect_inflated, __name__, print_info = print_info)
		
		insert(self, 'Depreciable Capital Costs', 'Total', 'Value', depreciable, __name__, print_info = print_info)
		insert(self, 'Depreciable Capital Costs', 'Inflated', 'Value', depreciable_inflated, __name__, print_info = print_info)
		
		capital.non_depreciable_capital_costs(self, print_info)

		non_depreciable_inflated = capital.non_depreciable * self.ci_inflator
		total = depreciable + capital.non_depreciable
		total_inflated = depreciable_inflated + non_depreciable_inflated

		insert(self, 'Non-Depreciable Capital Costs', 'Total', 'Value', capital.non_depreciable, __name__, print_info = print_info)
		insert(self, 'Non-Depreciable Capital Costs', 'Inflated', 'Value', non_depreciable_inflated, __name__, print_info = print_info)
		
		insert(self, 'Total Capital Costs', 'Total', 'Value', total, __name__, print_info = print_info)
		insert(self, 'Total Capital Costs', 'Inflated', 'Value', total_inflated, __name__, print_info = print_info)

	def direct_capital_costs(capital, self, print_info):

		capital.direct = sum_all_tables(self.inp, 'Direct Capital Cost', 'Value', insert_total = True, class_object = self, print_info = print_info)

	def indirect_capital_costs(capital, self, print_info):

		capital.indirect = sum_all_tables(self.inp, 'Indirect Capital Cost', 'Value', insert_total = True, class_object = self, print_info = print_info)

	def non_depreciable_capital_costs(capital, self, print_info):
		process_table(self.inp, 'Non-Depreciable Capital Costs', 'Value')

		non_depreciable = self.inp['Non-Depreciable Capital Costs']
		capital.non_depreciable = non_depreciable['Cost of land ($ per acre)']['Value'] * non_depreciable['Land required (acres)']['Value']
		capital.non_depreciable += sum_all_tables(self.inp, 'Other Non-Depreciable Capital Cost', 'Value', insert_total = True, class_object = self, print_info = print_info)


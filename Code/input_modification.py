import numbers
import copy
import pprint
from functools import lru_cache, reduce
import numpy as np
import operator
from timeit import default_timer as timer

def execute_plugin(plugin_name, plugs_dict, plugin_module = True, nested_dictionary = False, **kwargs):
	'''Exectue plugin named "plugin_name" and store plugin class object in "plugs_dict"'''

	if plugin_module is True:
		prefix = 'Plugins.'
	else:
		prefix = 'Analysis.'

	mod = __import__(prefix + plugin_name)
	plugin = getattr(mod, plugin_name)
	plugin_class = getattr(plugin, plugin_name)
	
	plugin_object = plugin_class(**kwargs)

	if nested_dictionary is True:
		plugs_dict[plugin_name] = {}
		plugs_dict[plugin_name]['Module'] = plugin_object
	else:
		plugs_dict[plugin_name] = plugin_object

	return plugin_object

@lru_cache(maxsize = None)
def read_textfile(file_name, delimiter, **kwargs):
	'''Wrapper for genfromtxt with lru_cache for repeated reads of the same file'''

	data = np.genfromtxt(file_name, delimiter = delimiter, **kwargs)

	return data

def num(s):
	'''Converting string to either an int, float, or, if neither is possible, returning the string.
	Input strings can contain commas as thousands seperators, which will be removed.
	If the input string ends with a "%" sign, it will be converted to a number divided by 100.
	'''
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

def convert_file_to_dictionary(file):
	'''Convert provided text file into dictionary. Text file has to follow GitHub flavoured Markdown style,
	specifically the table format:
	
	# Table A name

	First | Second | ...
	--- | --- | ---
	Entry A | value 1 | ...
	Entry B | value 2 | ...

	# Table B name

	...
	'''

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

def merge(a, b, path=None, update=True):
	'''Deep merge two dictionaries, with b having priority over a'''

	if path is None: path = []

	for key in b:
		if key in a:
			if isinstance(a[key], dict) and isinstance(b[key], dict):
				merge(a[key], b[key], path + [str(key)])
			elif a[key] == b[key]:
				pass # same leaf value
			elif isinstance(a[key], list) and isinstance(b[key], list):
				for idx, val in enumerate(b[key]):
					a[key][idx] = merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
			elif update:
				a[key] = b[key]
			else:
				raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
		
		else:
			a[key] = b[key]
	return a

def convert_input_to_dictionary(file, default = '../Config/Defaults.md'):
	'''Reads provided input file (file) and default file, converting both to dictionaries.
	The dictionaries are merged, with the input file having priority.
	Merged dictionary is returned
	'''

	inp_default = convert_file_to_dictionary(default)
	inp_file = convert_file_to_dictionary(file)

	return merge(inp_default, inp_file)

def get_by_path(root, items):
	'''Access a nested object in root by item sequence.'''
	return reduce(operator.getitem, items, root)

def set_by_path(root, items, value, value_type = 'value'):
	'''Set a value in a nested object in root by item sequence. Existing value is either multiplied
	by provided one (value_type = factor) or is replaced by provided one.

	In-place replacement, should only be used on deep copy of self.inp dictionary
	'''
	if value_type == 'factor':
		get_by_path(root, items[:-1])[items[-1]] *= value
	else:
		get_by_path(root, items[:-1])[items[-1]] = value

def insert(class_object, top_key, middle_key, bottom_key, value, name, print_info = True, add_processed = True):
	'''insert function used in plugins. 

	"inp" attribute of "class_object" is modified by inserting "value" at the position defined
	by top_key > middle_key > bottom_key.

	If there already is a value at this position, it will be overwritten. In this case, the 'Path' entry will be set
	to 'None' to avoid issues if value at this position already existed and had a path specified.

	If there is not already a value at this position,
	it will be created

	"name" is the name of plugin using "insert" for insertion.
	If "print_info" is True, action of "insert" will be printed.
	'''

	try:
		class_object.inp[top_key][middle_key][bottom_key] = value
		class_object.inp[top_key][middle_key]['Path'] = 'None' # setting path to "None" to avoid processing
		if print_info is True: print("'{0} > {1} > {2}' is being overwritten by {3}".format(top_key, middle_key, bottom_key, name))

	except KeyError:
		try:
			class_object.inp[top_key][middle_key] = {}
			class_object.inp[top_key][middle_key][bottom_key] = value
			if print_info is True: print("'{0} > {1}' is being created by {2}".format(top_key, middle_key, name))

		except KeyError:
			class_object.inp[top_key] = {}
			class_object.inp[top_key][middle_key] = {}
			class_object.inp[top_key][middle_key][bottom_key] = value
			if print_info is True: print("'{0}' is being created by {1}".format(top_key, name))

	if add_processed is True:
		class_object.inp[top_key][middle_key]['Processed'] = 'Yes'

def parse_parameter(key, delimiter = '>'):
	'''Provided "key" is split at delimiter(s) and returned as cleaned array'''

	key = str(key)

	path_components = key.split(delimiter)
	output = []

	for i in path_components:
		output.append(i.strip(' '))
		
	return output

def parse_parameter_to_list(key, delimiter):

	output = parse_parameter(key, delimiter = delimiter)

	lst = []

	for item in output:

		item = num(item)

		if item == 'True':
			item = True
		if item == 'False':
			item = False
		if item == 'None':
			item = None

		lst.append(item)

	return lst

def parse_parameter_to_array(key, delimiter = '>', dictionary = None, top_key = None, 
							 middle_key = None, bottom_key = None, special_values = [], path = None):
	'''parse_parameter() is applied to "key" string and result is converted to num and
	returned in NumPy array '''

	output = parse_parameter(key, delimiter = delimiter)
	array = []

	for i in output:
		if i in special_values:
			array.append(process_cell(dictionary, top_key, middle_key, bottom_key, 
						 cell = path, print_processing_warning = False))
		else:
			array.append(process_cell(dictionary, top_key, middle_key, bottom_key, 
						 cell = i, print_processing_warning = False))

	return np.asarray(array)

def parse_file_name(name):
	'''File name is extracted from provided path + file_name + extension'''

	file_name = name.split('/')
	file_name = file_name[-1].split('.')

	return file_name[0]

def process_path(dictionary, path, top_key, key, bottom_key, print_processing_warning = True):
	'''Processing provided path. Checks are performed to see if path is valid:
		1. If provided path contains no ">" symbols, it is not a path and 1 is returned
		2. If provided path contains only one ">" symbol, it is not a valid path. A warning is printed and 1 is returned.
		3. If provided path contains two ">" symbols, it is potentially a valid path. 
		   It is then attempted to retrieve target value. If retrieval attempt is unsuccessful, a warning is printed and 1 is returned.
		   If the path is valid, the target value is retrieved. 
		   	  If the rerieved target value comes from an unprocessed key, a warning is printed.
		   	  If the retrieved target value is non-numerical, a warning is printed and 1 is returned.
		   	  If the retrieved target value is numerical, it is returned.
	'''

	parsed_path = parse_parameter(path)

	if len(parsed_path) == 1:
		return 1.

	elif len(parsed_path) == 3:

		try:
			target_value = get_by_path(dictionary, parsed_path)

			if 'Processed' not in dictionary[parsed_path[0]][parsed_path[1]] and print_processing_warning is True:
				print('Warning: Unprocessed value is being used at "{0} > {1} > {2}" (by "{3} > {4}")'
					  .format(parsed_path[0], parsed_path[1], parsed_path[2], top_key, key))

			if not isinstance(target_value, numbers.Number):
				if isinstance(target_value, list) or type(target_value).__module__ == np.__name__:
					pass
				else:
					print('Warning: Non-numerical value retrieved at "{0} > {1} > {2}" (by "{3} > {4}"), setting to 1'
						  .format(parsed_path[0], parsed_path[1], parsed_path[2], top_key, key))
					target_value = 1.

		except KeyError:
			print('Warning: Invalid path specified for "{0}" (at "{1} > {2} > {3}"), setting to 1'
				  .format(path, top_key, key, bottom_key))
			target_value = 1.

		return target_value

	else:
		print('Warning: Invalid path specified for "{0}" (at "{1} > {2} > {3}"), setting to 1'
			   .format(path, top_key, key, bottom_key))
		return 1.

def process_cell(dictionary, top_key, key, bottom_key, cell = None, print_processing_warning = True):
	'''Processing of a single cell at dictionary[top_key][key][bottom_key]
	If cell contains only a number, the contents of that cell are returned. 
	If cell contains a string, but that string is not a path (indicated by absence of ">" symbol), 1 is returned
	If cell contains a string which is potentially a path, it is processed:
		Contents of the cell are split at ";" delimiter, separating multiple potential paths.
		For each potential path, process_path() is applied.
		The retrieved target value(s) are multiplied and returned.
			Since value is initated to 1, if none of the paths are valid, simply 1 is returned.
	'''
	if cell is None:
		cell = dictionary[top_key][key][bottom_key]

	if isinstance(cell, numbers.Number):
		return cell

	elif '>' not in cell:
		if isinstance(num(cell), numbers.Number):
			return num(cell)
		else:
			return 1.

	else:
		value = 1.
		paths = parse_parameter(cell, delimiter = ';')

		for path in paths:
			target_value = process_path(dictionary, path, top_key, key, bottom_key, 
								print_processing_warning = print_processing_warning)
			value *= target_value

		return value

def process_input(dictionary, top_key, key, bottom_key, path_key = 'Path', add_processed = True):
	'''
	Processing of input at dictionary[top_key][key][bottom_key] 

	Action: if there is an entry at dictionary[top_key][key][path_key], process_input() applies process_cell() 
	to dictionary[top_key][key][bottom_key] as well as dictionary[top_key][key][path_key] and multiplies them. 
	The resulting value is returned and placed into dictionary[top_key][key][bottom_key]

	Detailed Description:

	First, it is checked if that input has already been processed by looking for the "Processed" key.
	If this is the case, the input is simply returned.

	If it has not already been processed, it is checked if the input is a string which could not 
	be a path (not containing ">"). In this case the string is simply returned and "Processed" is added.

	If neither condition is met, process_cell() is applied. 
	It is then attempted to retrieve dictionary[top_key][key][path_key]. 
		If this entry cannot be retrieved, the process_cell() value of the input is returned,

		If this entry can be retrieved, process_cell() is applied to it and the resulting
		value is multiplied by the original process_cell() value of the input, updating value.

	If the obtained value differs from the original entry, the obtained value is inserted at
	dictionary[top_key][key][bottom_key] and the original entry is stored in
	dictionary[top_key][key][former_bottom_key] 

	At the end, "Processed" is added.
	'''

	entry = dictionary[top_key][key][bottom_key]

	if 'Processed' in dictionary[top_key][key]:
		return entry

	elif isinstance(entry, str) and '>' not in entry:
		if add_processed is True:
			dictionary[top_key][key]['Processed'] = 'Yes'
		return entry

	else:
		value = process_cell(dictionary, top_key, key, bottom_key)

		try:
			target_value = process_cell(dictionary, top_key, key, path_key)
			value *= target_value
		except KeyError:
			pass

		#if value != dictionary[top_key][key][bottom_key]:
		if np.array_equal(value, dictionary[top_key][key][bottom_key]) is False:
			former_bottom_key = 'Former ' + bottom_key 
			dictionary[top_key][key][former_bottom_key] = dictionary[top_key][key][bottom_key]
			dictionary[top_key][key][bottom_key] = value  # setting dictionary entry to obtained value
		
		if add_processed is True:
			dictionary[top_key][key]['Processed'] = 'Yes'   # marking that this key has been processed

		return value

def process_table(dictionary, top_key, bottom_key, path_key = 'Path'):
	'''Looping through all keys in dictionary[top_key] and applying process_input to
	dictionary[top_key][key][bottom_key]
	
	bottom_key can also be an array of keys, all of which are processed (in this case, path_key has to be an
	array of equal length). 
	'''

	for key in dictionary[top_key]:

		if isinstance(bottom_key, str):
			value = process_input(dictionary, top_key, key, bottom_key, path_key = path_key)

		else:
			for single_key, path in zip(bottom_key[:-1], path_key[:-1]):
				value = process_input(dictionary, top_key, key, single_key, path_key = path, add_processed = False)

			process_input(dictionary, top_key, key, bottom_key[-1], path_key = path_key[-1], add_processed = True)

def sum_table(dictionary, top_key, bottom_key, path_key = 'Path'):
	'''For the provided "dictionary", all entries in dictionary[top_key] are processed using "process_input" (positions:
	top_key > key > bottom key) and summed.
	'''

	value = 0.

	for key in dictionary[top_key]:
		value += process_input(dictionary, top_key, key, bottom_key, path_key = path_key)

	return value

def sum_all_tables(dictionary, table_group, bottom_key, insert_total = False, class_object = None, middle_key_insertion = 'Summed Total', bottom_key_insertion = 'Value', print_info = True, path_key = 'Path', return_contributions = False):
	'''Applies sum_table() to all dictionary entries with a key that contains "table_group". Resulting sum_table()
	values are summed to return total.

	If "insert_total" is true, the sum_table() value for a given key is inserted in class_object.inp at 
	key > middle_key_insertion > bottom_key_insertion.

	The contributions of each table in table_group are stored in "contributions" dictionary, which is returned
	if "return_contributions" is set to True. Dictionary is structured so that it can be probided to "Cost_Contributions"
	class to generate a cost breakdown plot.
	'''

	total = 0.
	contributions = {}
	contributions['Data'] = {}

	for key in dictionary:

		if table_group in key:
			value = sum_table(dictionary, key, bottom_key, path_key = path_key)
			total += value
			contributions['Data'][key] = value

			if insert_total is True:
				insert(class_object, key, middle_key_insertion, bottom_key_insertion, value, __name__, print_info = print_info)

	contributions['Total'] = total
	contributions['Table Group'] = table_group

	if return_contributions is True:
		return total, contributions
	else:
		return total
import numbers

def insert(class_object, top_key, middle_key, bottom_key, value, name, print_info = True):
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

	class_object.inp[top_key][middle_key]['Processed'] = 'Yes'

def parse_parameter(key, delimiter = '>'):
	'''Provided "key" is split at delimiter(s) and returned as cleaned array'''

	path_components = key.split(delimiter)
	output = []

	for i in path_components:
		output.append(i.strip(' '))
		
	return output

def process_path(dictionary, path, top_key, key, bottom_key):
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
			target_value = dictionary[parsed_path[0]][parsed_path[1]][parsed_path[2]]
		except KeyError:
			print('Warning: Invalid path specified for "{0}" (at "{1} > {2} > {3}"), setting to 1'.format(path, top_key, key, bottom_key))
			target_value = 1.

		if 'Processed' not in dictionary[parsed_path[0]][parsed_path[1]]:
			print('Warning: Unprocessed value is being used at "{0} > {1} > {2}" (by "{3} > {4}")'.format(parsed_path[0], parsed_path[1], parsed_path[2], top_key, key))

		if not isinstance(target_value, numbers.Number):
			print('Warning: Non-numerical value retrieved at "{0} > {1} > {2}" (by "{3} > {4}"), setting to 1'.format(parsed_path[0], parsed_path[1], parsed_path[2], top_key, key))
			target_value = 1.

		return target_value

	else:
		print('Warning: Invalid path specified for "{0}" (at "{1} > {2} > {3}"), setting to 1'.format(path, top_key, key, bottom_key))
		return 1.

def process_cell(dictionary, top_key, key, bottom_key):
	'''Processing of a single cell at dictionary[top_key][key][bottom_key]
	If cell contains only a number, the contents of that cell are returned. 
	If cell contains a string, but that string is not a path (indicated by absence of ">" symbol), 1 is returned
	If cell contains a string which is potentially a path, it is processed:
		Contents of the cell are split at ";" delimiter, separating multiple potential paths.
		For each potential path, process_path() is applied.
		The retrieved target value(s) are multiplied and returned.
			Since value is initated to 1, if none of the paths are valid, simply 1 is returned.
	'''

	cell = dictionary[top_key][key][bottom_key]

	if isinstance(cell, numbers.Number):
		return cell

	elif '>' not in cell:
		return 1.

	else:
		value = 1.
		paths = parse_parameter(cell, delimiter = ';')

		for path in paths:
			target_value = process_path(dictionary, path, top_key, key, bottom_key)
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
		dictionary[top_key][key]['Processed'] = 'Yes'
		return entry

	else:
		value = process_cell(dictionary, top_key, key, bottom_key)

		try:
			target_value = process_cell(dictionary, top_key, key, path_key)
			value *= target_value
		except KeyError:
			pass

		if value != dictionary[top_key][key][bottom_key]:
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

def sum_all_tables(dictionary, table_group, bottom_key, insert_total = False, class_object = None, middle_key_insertion = 'Summed Total', bottom_key_insertion = 'Value', print_info = True, path_key = 'Path'):
	'''Applies sum_table() to all dictionary entries with a key that contains "table_group". Resulting sum_table()
	values are summed to return total.

	If "insert_total" is true, the sum_table() value for a given key is inserted in class_object.inp at 
	key > middle_key_insertion > bottom_key_insertion
	'''

	total = 0.

	for key in dictionary:

		if table_group in key:
			value = sum_table(dictionary, key, bottom_key, path_key = 'Path')
			total += value

			if insert_total is True:
				insert(class_object, key, middle_key_insertion, bottom_key_insertion, value, __name__, print_info = print_info)

	return total
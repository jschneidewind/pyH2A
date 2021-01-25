def insert(class_object, top_key, middle_key, bottom_key, value, name, print_info = True):

	try:
		class_object.inp[top_key][middle_key][bottom_key] = value
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

from scipy import constants as con

def nm(value):
	'''Converts nm to J'''
	return ((con.h*con.c)/(value/1e9))

def eV(value):
	'''Converts eV to J'''
	return value*1.602176e-19

def kcalmol(value):
	'''Converts kcal/mol to J'''
	return (value * 4186.798188)/con.Avogadro

def Jmol(value):
	'''Converts J/mol to J'''
	return value / con.Avogadro

def kWh(value):
	'''Converts kWh to J'''
	return value * 3.6e6

def J(value):
	'''Converts J to J'''
	return value

def kJmol(value):
	'''Converts kJ/mol to J'''
	return (1e3 * value) / con.Avogadro

class Energy:
	'''Energy class to convert between different energy units.

	Parameters
	----------
	value : float
		Input energy value.
	unit : function
		Unit name which corresponds to the one of the functions defined
		outside of the class. This function is used to convert
		the input energy value to Joule.

	Notes
	-----
	Input value in either nm, eV, kcal/mol, J/mol, kJ/mol, kWh or J.
	Available units: J, eV, nm, kcal/mol, J/mol, kWh, kJ/mol.
	Once an Energy class object has been generated, the energy 
	value in the desired unit can be retrieved using the appropriate class
	attribute.
	'''

	def __init__(self, value, unit):
		self.unit = unit.__name__
		self.value = value

		self.J = unit(self.value)
		self.eV = self.convert_J_to_eV()
		self.nm = self.convert_J_to_nm()
		self.kcalmol = self.convert_J_to_kcalmol()
		self.Jmol = self.convert_J_to_Jmol()
		self.kWh = self.convert_J_to_kWh()
		self.kJmol = self.convert_J_to_kJmol()

	def convert_J_to_eV(self):
		'''Convert J to eV'''
		return self.J/1.602176e-19

	def convert_J_to_nm(self):
		'''Convert J to nm'''
		return ((con.h*con.c)/self.J)*1e9

	def convert_J_to_kcalmol(self):
		'''Convert J to kcal/mol'''
		return (self.J * con.Avogadro)/4186.798188

	def convert_J_to_Jmol(self):
		'''Convert J to J/mol'''
		return self.J * con.Avogadro

	def convert_J_to_kWh(self):
		'''Convert J to kWh'''
		return self.J/3.6e6

	def convert_J_to_kJmol(self):
		'''Convert to J to kJ/mol'''
		return (self.J * con.Avogadro) / 1e3
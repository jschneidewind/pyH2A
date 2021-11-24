from scipy import constants as con

def nm(value):
	'''Converts nm to J'''
	return ((con.h*con.c)/(value/1e9))

def eV(value):
	'''Converts eV to J'''
	return value*1.602176e-19

def kcalmol(value):
	'''Converts kcalmol to J'''
	return (value * 4186.798188)/con.Avogadro

def Jmol(value):
	'''Converts Jmol to J'''
	return value / con.Avogadro

def kWh(value):
	'''Converts kWh to J'''
	return value * 3.6e6

def J(value):
	'''Converts J to J'''
	return value

def kJmol(value):
	'''Converts kJmol to J'''
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
	Input value in either nm, eV, kcalmol, Jmol, kWh or J
	Available units: J, eV, nm, kcal/mol, J/mol, kWh
	Once an Energy class object has been generated, the energy 
	value in the desired unit can be retrieved using the appropriate class
	attribute.

	Methods
	-------
	convert_J_to_eV:
		J to eV.
	convert_J_to_nm:
		J to nm.
	convert_J_to_kcalmol:
		J to kcal/mol.
	convert_J_to_Jmol:
		J to J/mol
	convert_J_to_kWh:
		J to kWh.
	convert_J_to_kJmol:
		J to kJ/mol.
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
		return self.J/1.602176e-19

	def convert_J_to_nm(self):
		return ((con.h*con.c)/self.J)*1e9

	def convert_J_to_kcalmol(self):
		return (self.J * con.Avogadro)/4186.798188

	def convert_J_to_Jmol(self):
		return self.J * con.Avogadro

	def convert_J_to_kWh(self):
		return self.J/3.6e6

	def convert_J_to_kJmol(self):
		return (self.J * con.Avogadro) / 1e3
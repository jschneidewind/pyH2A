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
	'''Convert Jmol to J'''
	return value / con.Avogadro

def kWh(value):
	'''Converts kWh to J'''
	return value * 3.6e6

def J(value):
	'''Convert J to J'''
	return value

def kJmol(value):
	'''Convert kJmol to J'''
	return (1e3 * value) / con.Avogadro

class Energy:

	def __init__(self, value, unit):
		'''Input value in either nm, eV, kcalmol, Jmol, kWh or J
		Available units: J, eV, nm, kcal/mol, J/mol, kWh'''
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
import numpy as np
from pyH2A.Utilities.Energy_Conversion import Energy, kWh, eV
from pyH2A.Utilities.input_modification import insert, process_table

class PEC_Plugin:
	'''Simulating H2 production using photoelectrochemical water splitting.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output in (kg of H2)/day, ``process_table()`` is used.
	PEC Cells > Cell Cost ($/m2) > Value : float
		Cost of PEC cells in $/m2.
	PEC Cells > Lifetime (year) > Value : float
		Lifetime of PEC cells in years before replacement is required.
	PEC Cells > Length (m) > Value : float
		Length of single PEC cell in m.
	PEC Cells > Width (m) > Value : float
		Width of single PEC cell in m.
	Land Area Requirement > Cell Angle (degree) > Value : float
		Angle of PEC cells from the ground, in degrees.
	Land Area Requirement > South Spacing (m) > Value : float
		South spacing of PEC cells in m.
	Land Ares Requirement > East/West Spacing (m) > Value : float
		East/West Spacing of PEC cells in m.
	Solar-to-Hydrogen Efficiency > STH (%) > Value : float
		Solar-to-hydrogen efficiency in percentage or as a value between 0 and 1.
	Solar Input > Mean solar input (kWh/m2/day) > Value : float
		Mean solar input in kWh/m2/day, ``process_table()`` is used.
	Solar Concentrator > Concentration Factor > Value : float, optional
		Concentration factor created by solar concentration module, which is used in combination
		with PEC cells. If "Solar Concentrator" is in dcf.inp, ``process_table()`` is used.

	Returns
	-------
	Non-Depreciable Capital Costs > Land required (acres) > Value : float
		Total land area required in acres.
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
		Solar collection area in m2.
	Planned Replacement > Planned Replacement PEC Cells > Cost ($) : float
		Total cost of replacing all PEC cells once.
	Planned Replacement > Planned Replacement PEC Cells > Frequency (years) : float
		Replacement frequency of PEC cells in years, identical to PEC cell lifetime.
	Direct Capital Costs - PEC Cells > PEC Cell Cost ($) > Value : float
		Total cost of all PEC cells.
	PEC Cells > Number > Value : float
		Number of individual PEC cells required for design H2 output capacity.
	'''

	def __init__(self, dcf, print_info):
		if 'Solar Concentrator' in dcf.inp:
			process_table(dcf.inp, 'Solar Concentrator', 'Value')

		process_table(dcf.inp, 'Solar Input', 'Value')
		process_table(dcf.inp, 'Solar-to-Hydrogen Efficiency', 'Value')
		process_table(dcf.inp, 'PEC Cells', 'Value')
		process_table(dcf.inp, 'Land Area Requirement', 'Value')
		process_table(dcf.inp, 'Technical Operating Parameters and Specifications', 'Value')

		self.hydrogen_production(dcf)
		self.PEC_cost(dcf)
		self.land_area(dcf)

		insert(dcf, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', 
		       self.total_land_area_acres, __name__, print_info = print_info)
		insert(dcf, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', 
			   self.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(dcf, 'Planned Replacement', 'Planned Replacement PEC Cells', 'Cost ($)', 
			   self.cell_cost, __name__, print_info = print_info)
		insert(dcf, 'Planned Replacement', 'Planned Replacement PEC Cells', 'Frequency (years)', 
			   dcf.inp['PEC Cells']['Lifetime (years)']['Value'], __name__, print_info = print_info)

		insert(dcf, 'Direct Capital Costs - PEC Cells', 'PEC Cell Cost ($)', 'Value', 
			   self.cell_cost, __name__, print_info = print_info)

		insert(dcf, 'PEC Cells', 'Number', 'Value', self.cell_number, __name__, print_info = print_info)

	def hydrogen_production(self, dcf):
		'''Calculation of (kg of H2)/day produced by single PEC cell.
		'''

		pec = dcf.inp['PEC Cells']

		self.cell_area = pec['Length (m)']['Value'] * pec['Width (m)']['Value']
		cell_insolation = Energy(self.cell_area * dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_cell = (cell_insolation.J * dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		self.kg_H2_per_cell = (2 * mol_H2_per_cell) / 1000.

	def PEC_cost(self, dcf):
		'''Calculation of cost per cell, number of required cells and total cell cost.
		'''

		cost_per_cell = self.cell_area * dcf.inp['PEC Cells']['Cell Cost ($/m2)']['Value']
		self.cell_number = np.ceil(dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / self.kg_H2_per_cell)
		self.cell_cost = self.cell_number * cost_per_cell

	def land_area(self, dcf):
		'''Calculation of total required land area and solar collection area.
		'''

		land = dcf.inp['Land Area Requirement']
		pec = dcf.inp['PEC Cells']

		self.total_solar_collection_area = self.cell_area * self.cell_number

		cell_plan_view = pec['Length (m)']['Value'] * np.cos(np.radians(land['Cell Angle (degree)']['Value']))
		total_length = cell_plan_view + land['South Spacing (m)']['Value']	
		total_width = pec['Width (m)']['Value'] + land['East/West Spacing (m)']['Value']

		self.total_land_area = total_width * total_length * self.cell_number
		self.total_land_area_acres = self.total_land_area * 0.000247105
		
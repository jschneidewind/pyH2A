import numpy as np
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.Utilities.Energy_Conversion import Energy, kWh, eV


class PECPlugin(Plugin):
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
	Land Area Requirement > East/West Spacing (m) > Value : float
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

	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = [
			'Solar Input', 
			'Solar-to-Hydrogen Efficiency', 
			'PEC Cells', 
			'Land Area Requirement', 
			'Technical Operating Parameters and Specifications'
		]
		if 'Solar Concentrator' in self.dcf.inp:
			table_keys.append('Solar Concentrator')
		self.process_table(table_keys)
		self.run_plugin()
		self.process_insert_queue()

	def run_plugin(
			self
			) -> None:
		tea = PECPluginTEA(self)
		tea.hydrogen_production()
		tea.PEC_cost()
		tea.land_area()


class PECPluginTEA:
	'''Handles life-cycle assessment (LCA) calculations for the PEC plugin.
	'''
	def __init__(
			self,
			plugin: PECPlugin
			) -> None:
		self.plugin: PECPlugin = plugin

	def hydrogen_production(
			self
			) -> None:
		'''Calculation of (kg of H2)/day produced by single PEC cell.
		'''
		pec = self.plugin.dcf.inp['PEC Cells']

		self.cell_area = pec['Length (m)']['Value'] * pec['Width (m)']['Value']
		cell_insolation = Energy(self.cell_area * self.plugin.dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_cell = (cell_insolation.J * self.plugin.dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		self.kg_H2_per_cell = (2 * mol_H2_per_cell) / 1000.
		self.mol_H2_per_m2_per_day = mol_H2_per_cell / self.cell_area

	def PEC_cost(
			self
			) -> None:
		'''Calculation of cost per cell, number of required cells and total cell cost.
		'''

		cost_per_cell = self.cell_area * self.plugin.dcf.inp['PEC Cells']['Cell Cost ($/m2)']['Value']
		self.cell_number = np.ceil(self.plugin.dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / self.kg_H2_per_cell)
		self.cell_cost = self.cell_number * cost_per_cell

		self.plugin.insert_queue.extend([
			{'key': 'PEC Cells', 'subkey': 'Number', 'value': self.cell_number},
			{'key': 'Direct Capital Costs - PEC Cells', 'subkey': 'PEC Cell Cost ($)', 'value': self.cell_cost},
			{'key': 'Planned Replacement', 'subkey': 'Planned Replacement PEC Cells', 'field': 'Cost ($)', 'value': self.cell_cost, 'mod': __name__, 'print_info': self.plugin.dcf.print_info},
			{'key': 'Planned Replacement', 'subkey': 'Planned Replacement PEC Cells', 'field': 'Frequency (years)', 'value': self.plugin.dcf.inp['PEC Cells']['Lifetime (years)']['Value'], 'mod': __name__, 'print_info': self.plugin.dcf.print_info}
		])

	def land_area(
			self
			) -> None:
		'''Calculation of total required land area and solar collection area.
		'''
		land = self.plugin.dcf.inp['Land Area Requirement']
		pec = self.plugin.dcf.inp['PEC Cells']

		total_solar_collection_area = self.cell_area * self.cell_number

		cell_plan_view = pec['Length (m)']['Value'] * np.cos(np.radians(land['Cell Angle (degree)']['Value']))
		total_length = cell_plan_view + land['South Spacing (m)']['Value']	
		total_width = pec['Width (m)']['Value'] + land['East/West Spacing (m)']['Value']

		self.total_land_area = total_width * total_length * self.cell_number
		total_land_area_acres = self.total_land_area * 0.000247105
		self.plugin.insert_queue.extend([
			{'key': 'Non-Depreciable Capital Costs', 'subkey': 'Land required (acres)', 'value': total_land_area_acres},
			{'key': 'Non-Depreciable Capital Costs', 'subkey': 'Solar Collection Area (m2)', 'value': total_solar_collection_area}
		])


class PECPluginLCA:
	
    def __init__(
            self, 
            plugin: PECPlugin
            ) -> None:
        self.plugin: PECPlugin = plugin
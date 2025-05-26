from pyH2A.Utilities.Energy_Conversion import Energy, kWh, eV
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins.Plugin import Plugin


class SolarThermalPlugin(Plugin):
	'''Simulation of hydrogen production using solar thermal water splitting.

	Parameters
	----------
	Technical Operating Parameters and Specifications > Design Output per Day > Value : float
		Design output of hydrogen production plant per day in kg.
	Solar-to-Hydrogen Efficiency > STH (%) > Value : float
		Solar-to-Hydrogen Efficiency of thermal water splitting process. Percentage of value 
		between 0 and 1.
	Solar Input > Mean solar input (kWh/m2/day) > Value : float
		Mean solar input in kWh/m2/day.
	Non-Depreciable Capital Costs > Additional Land Area (%) > Value : float
		Additional land area required. Percentage or value > 0. Calculated as:
		(1 + Addtional Land Area) * solar collection area.

	Returns
	-------
	Non-Depreciable Capital Costs > Land required (acres) > Value : float
		Total land requirement in acres.
	'''
	
	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = ['Technical Operating Parameters and Specifications', 'Solar-to-Hydrogen Efficiency', 'Solar Input', 'Non-Depreciable Capital Costs']
		self.process_table(table_keys)
		self.run_plugin()
		self.insert_table()
		
	def run_plugin(
			self
			) -> None:
		tea = SolarThermalPluginTEA(self)
		tea.calculate_land_area()


class SolarThermalPluginTEA:

	def __init__(
			self,
			plugin: SolarThermalPlugin
			) -> None:
		self.plugin: SolarThermalPlugin = plugin

	def calculate_land_area(self):
		'''Calculation of required land area based on solar input, solar-to-hydrogen efficiency
		and addtional land are requirements.
		'''

		insolation_per_m2_per_day = Energy(self.dcf.inp['Solar Input']['Mean solar input (kWh/m2/day)']['Value'], kWh)

		mol_H2_per_m2_per_day = (insolation_per_m2_per_day.J * self.dcf.inp['Solar-to-Hydrogen Efficiency']['STH (%)']['Value']) / Energy(2*1.229, eV).Jmol
		kg_H2_per_m2_per_day = (2 * mol_H2_per_m2_per_day)/1000.

		required_area_m2 = self.dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value'] / kg_H2_per_m2_per_day

		area_m2 = required_area_m2 * (1. + self.dcf.inp['Non-Depreciable Capital Costs']['Additional Land Area (%)']['Value'])
		area_acres = area_m2 * 0.000247105
		self.plugin.insert_queue.append(
			{'key': 'Non-Depreciable Capital Costs', 'subkey': 'Land required (acres)', 'value': area_acres}
		)


class SolarThermalPluginLCA:
	
    def __init__(
            self, 
            plugin: SolarThermalPlugin
            ) -> None:
        self.plugin: SolarThermalPlugin = plugin

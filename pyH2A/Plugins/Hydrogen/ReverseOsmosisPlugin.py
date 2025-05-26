from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
import numpy as np

MOLAR_RATIO_WATER = 18.01528 / 2.016
MOLAR_RATIO_O2_H2 = 31.999 / 2.016
DENSITY_WATER_KG_PER_M3 = 997

class ReverseOsmosisPlugin(Plugin):
	'''Simulation of purified water production using reverse osmosis.
	
	Parameters
	----------
	Financial Input Values > construction time > Value : int
		Construction time of hydrogen production plant in years.
	Technical Operating Parameters and Specifications > Output per Year > Value : float
		Yearly output taking operating capacity factor into account, in (kg of H2)/year.
	Reverse Osmosis > Power Demand (kWh/m3) > Value : float
		Power demand of reverse osmosis plant in kWh per m3 of sea water.
	Reverse Osmosis > Average daily operating hours > Value : float
		Average daily operating hours of reverse osmosis plant, used for scaling of reverse osmosis plant.
	Reverse Osmosis > Recovery Rate > Value : float
		Fraction of fresh water obtained from given volume of sea water.
  
    Returns
    -------
    Power Consumption > Reverse Osmosis Consumption (kWh, yearly) > Value : nd.array
        Electricity demand of reverse osmosis plant in kWh per year.
    Power Consumption > Reverse Osmosis Consumption (kWh, yearly) > Type : str
        Type of power consumer, type is 'flexible', uses both stored and available power.
    Reverse Osmosis > Capacity (m3/h) > Value : float
        Maximum sea water processing capacity per hour of reverse osmosis plant.
    LCA - Exports > Deionised Water Weight > Value : float
        Weight of deionised water produced in kg.
    '''

	def __init__(
			self, 
			dcf: DiscountedCashFlow
			) -> None:
		super().__init__(dcf)

		table_keys = ['Reverse Osmosis', 'Technical Operating Parameters and Specifications']
		self.process_table(table_keys)
		self.run_plugin()
		self.process_insert_queue()

	def run_plugin(
			self
			) -> None:
		tea = ReverseOsmosisPluginTEA(self)
		lca = ReverseOsmosisPluginLCA(self)

		tea.calculate_electricity_demand()
		tea.calculate_reverse_osmosis_scaling()
		lca.export_fresh_water_weight()
		
class ReverseOsmosisPluginTEA:
	'''Handles life-cycle assessment (LCA) calculations for the reverse osmosis plugin.
	'''
	def __init__(
			self,
			plugin: ReverseOsmosisPlugin
			) -> None:
		self.plugin: ReverseOsmosisPlugin = plugin

	def calculate_electricity_demand(
			self
			) -> None:
		'''Calculation of electricity demand for reverse osmosis based on
		yearly amount of hydrogen production.
		'''
		self.plugin.h2_produced_per_year_kg = self.plugin.dcf.inp['Technical Operating Parameters and Specifications']['Output per Year']['Value']

		self.plugin.fresh_water_demand_kg = self.plugin.h2_produced_per_year_kg * MOLAR_RATIO_WATER
		fresh_water_demand_m3 = self.plugin.fresh_water_demand_kg / DENSITY_WATER_KG_PER_M3

		self.plugin.sea_water_demand_m3 = fresh_water_demand_m3 / self.plugin.dcf.inp['Reverse Osmosis']['Recovery Rate']['Value']

		electricity_demand_kWh = self.plugin.sea_water_demand_m3 * self.plugin.dcf.inp['Reverse Osmosis']['Power Demand (kWh/m3)']['Value']
		self.electricity_demand_kWh = electricity_demand_kWh[self.plugin.dcf.inp['Financial Input Values']['construction time']['Value']:]

		self.plugin.insert_queue.append(
			{'key': 'Power Consumption', 'subkey': 'Reverse Osmosis Consumption (kWh, yearly)', 'value': self.electricity_demand_kWh}
		)

	def calculate_reverse_osmosis_scaling(
			self
			) -> None:
		'''
		Calculation of maximum sea water processing capacity per hour based on
		yearly sea water demand and average daily operating hours.
		'''

		DAYS_IN_A_YEAR = 365

		average_daily_operating_hours = self.plugin.dcf.inp['Reverse Osmosis']['Average daily operating hours']['Value']
		yearly_operating_hours = average_daily_operating_hours * DAYS_IN_A_YEAR
		
		try:
			maximum_yearly_sea_water_demand_m3 = max(self.plugin.sea_water_demand_m3)
		except TypeError:
			maximum_yearly_sea_water_demand_m3 = self.plugin.sea_water_demand_m3

		maximum_sea_water_processing_m3_per_hour = maximum_yearly_sea_water_demand_m3 / yearly_operating_hours
		self.plugin.insert_queue.extend([
			{'key': 'Reverse Osmosis', 'subkey': 'Capacity (m3/h)', 'value': maximum_sea_water_processing_m3_per_hour},
			{'key': 'Power Consumption', 'subkey': 'Reverse Osmosis Consumption (kWh, yearly)', 'field': 'Type', 'value': 'flexible', 'mod': __name__}
		])
		
class ReverseOsmosisPluginLCA:

	def __init__(
			self, 
			plugin: ReverseOsmosisPlugin
			) -> None:
		self.plugin = plugin
	
	def export_fresh_water_weight(
			self
			) -> None:
		'''Export the weight of the fresh water.'''
		fresh_water_weight = np.sum(self.plugin.fresh_water_demand_kg)
		self.plugin.insert_queue.append(
			{'key': 'LCA - Exports', 'subkey': 'Deionised Water Weight', 'value': fresh_water_weight}
		)
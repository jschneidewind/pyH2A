from pyH2A.Utilities.input_modification import insert, process_table

class Solar_Concentrator_Plugin:
	'''Simulation of solar concentration (used in combination with PEC cells).

	Parameters
	----------
	Solar Concentrator > Concentration Factor > Value : float
		Concentration factor of solar concentration, value > 1.
	Solar Concentrator > Cost ($/m2) > Value : float
		Cost of solar concentrator in $/m2.
	PEC Cells > Number > Value : float
		Number of PEC cells required for design H2 production capacity.
	Land Area Requirement > South Spacing (m) > Value : float
		South spacing of solar concentrators in m.
	Land Area Requirement > East/West Spacing (m) > Value : float
		East/West Spacing (m) of solar concentrators in m.
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
		Total solar collection area in m2.

	Returns
	-------
	Non-Depreciable Capital Costs > Land required (acres) > Value : float
		Total land requirement in acres.
	Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
		Total solar collection area in m2.
	Direct Capital Costs - Solar Concentrator > Solar Concentrator Cost ($) > Value : float
		Total cost of all solar concentrators.
	'''

	def __init__(self, dcf, print_info):
		process_table(dcf.inp, 'Solar Concentrator', 'Value')
		process_table(dcf.inp, 'PEC Cells', 'Value')
		process_table(dcf.inp, 'Land Area Requirement', 'Value')
		process_table(dcf.inp, 'Non-Depreciable Capital Costs', 'Value')

		self.land_area(dcf)
		self.calculate_cost(dcf)

		insert(dcf, 'Non-Depreciable Capital Costs', 'Land required (acres)', 'Value', 
				self.total_land_area_acres, __name__, print_info = print_info)
		insert(dcf, 'Non-Depreciable Capital Costs', 'Solar Collection Area (m2)', 'Value', 
				self.total_solar_collection_area, __name__, print_info = print_info)
		
		insert(dcf, 'Direct Capital Costs - Solar Concentrator', 'Solar Concentrator Cost ($)', 'Value', 
				self.concentrator_cost, __name__, print_info = print_info)

	def land_area(self, dcf):
		'''Calculation of solar collection area by multiplying concentration factor by supplied
		(unconcentrated) solar collection area. Calculation of total land area requirement based
		on number of PEC cells and spacing of solar concentrators.
		'''

		land = dcf.inp['Land Area Requirement']

		self.total_solar_collection_area = dcf.inp['Solar Concentrator']['Concentration Factor']['Value'] * dcf.inp['Non-Depreciable Capital Costs']['Solar Collection Area (m2)']['Value']

		self.total_land_area = land['South Spacing (m)']['Value'] * land['East/West Spacing (m)']['Value'] * dcf.inp['PEC Cells']['Number']['Value']
		self.total_land_area_acres = self.total_land_area * 0.000247105

	def calculate_cost(self, dcf):
		'''Calculation of solar concentrator cost based on cost per m2 and total solar collection area.
		'''

		self.concentrator_cost = dcf.inp['Solar Concentrator']['Cost ($/m2)']['Value'] * self.total_solar_collection_area

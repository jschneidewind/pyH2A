from pyH2A.run_pyH2A import pyH2A
from scipy.stats import ttest_ind
import pprint

def pv_e_base():
	
	result = pyH2A('./PV_E/Base/PV_E_Base.md', './PV_E/Base')
	pprint.pprint(result.meta_modules['Monte_Carlo_Analysis']['Module'].shortest_target_distance)

	#pprint.pprint(result.__dict__)

	#pprint.pprint(result.base_case.inp)

	#pprint.pprint(result.base_case.inp['Direct Capital Costs - Electrolyzer'])
	#pprint.pprint(result.base_case.inp['Planned Replacement'])

def pv_e_limit():
	result = pyH2A('./PV_E/Limit/PV_E_Limit.md', './PV_E/Limit')

def pv_e_distance_time():
	result = pyH2A('./PV_E/Historical_Data/PV_E_Distance_Time.md', './PV_E/Historical_Data')

	print(result.meta_modules['Development_Distance_Time_Analysis']['Module'].p_linear)

def pec_base():

	result = pyH2A('./PEC/Base/PEC_Base.md', './PEC/Base')
	#pprint.pprint(result.base_case.inp['Non-Depreciable Capital Costs'])
	pprint.pprint(result.meta_modules['Monte_Carlo_Analysis']['Module'].shortest_target_distance)

def pec_limit():
	
	result = pyH2A('./PEC/Limit/PEC_Limit.md', './PEC/Limit')

	pprint.pprint(result.base_case.plugs['PEC_Plugin'].mol_H2_per_m2_per_day*3/24.)
	pprint.pprint(result.base_case.plugs['PEC_Plugin'].mol_H2_per_m2_per_day)
	pprint.pprint(result.base_case.plugs['PEC_Plugin'].total_solar_collection_area)


	#pprint.pprint(result.base_case.inp['Direct Capital Costs - Solar Concentrator'])
	#pprint.pprint(result.base_case.inp['Non-Depreciable Capital Costs'])
	#pprint.pprint(result.base_case.inp['PEC Cells']['Number'])

def pec_limit_no_concentration():

	result = pyH2A('./PEC/No_Conc/PEC_Limit_No_Concentration.md', './PEC/No_Conc')

	#pprint.pprint(result.base_case.inp['Non-Depreciable Capital Costs'])

def photocatalytic_base():
	#225.15652501997127 $/kg
	
	result = pyH2A('./Photocatalytic/Base/Photocatalytic_Base.md', './Photocatalytic/Base')
	

	pprint.pprint(result.meta_modules['Monte_Carlo_Analysis']['Module'].shortest_target_distance)
	#pprint.pprint(result.base_case.plugs['Photocatalytic_Plugin'].catalyst_amount_kg)
	#pprint.pprint(result.base_case.inp['Reactor Baggies'])
	#pprint.pprint(result.base_case.inp['Direct Capital Costs - Reactor Baggies'])
	#pprint.pprint(result.base_case.inp['Direct Capital Costs - Control System']['Hydrogen Area Sensors ($ per baggie)'])


	# from pyH2A.Discounted_Cash_Flow import discounted_cash_flow_function
	# import matplotlib.pyplot as plt
	# import numpy as np
	# data_points = np.arange(100, 10000, 100)
	# results = discounted_cash_flow_function('./Photocatalytic/Base/Photocatalytic_Base.md', 
	# 										data_points,
	# 										np.array(['Reactor Baggies', 'Length (m)', 'Value']))
	# plt.plot(data_points, results, 'o-')
	# plt.show()

def photocatalytic_limit():

	result = pyH2A('./Photocatalytic/Limit/Photocatalytic_Limit.md', './Photocatalytic/Limit')
	pprint.pprint(result.base_case.plugs['Photocatalytic_Plugin'].catalyst_properties)

def technology_comparison():
	pec = pyH2A('./PEC/Base/PEC_Base.md', './PEC/Base')
	pc =  pyH2A('./Photocatalytic/Base/Photocatalytic_Base.md', './Photocatalytic/Base')
	pv_e =  pyH2A('./PV_E/Base/PV_E_Base.md', './PV_E/Base')

	pec_distances = pec.meta_modules['Monte_Carlo_Analysis']['Module'].distances
	pc_distances = pc.meta_modules['Monte_Carlo_Analysis']['Module'].distances
	pv_e_distances = pv_e.meta_modules['Monte_Carlo_Analysis']['Module'].distances

	print(ttest_ind(pv_e_distances, pc_distances))




def test():

	from pyH2A.Utilities.Energy_Conversion import Energy, eV, J, kJmol
	from scipy import constants as con

	reaction_energy_per_kg = Energy(2*1.229*con.Avogadro* (1000./2.), eV)
	print(reaction_energy_per_kg.J/1e6)
	print(Energy(141 * 1e6, J).kWh)
	print(Energy(285.83 * (1000./2.) * con.Avogadro, kJmol).J)

def main():
	pv_e_base()
	#pv_e_limit()
	#pv_e_distance_time()
	#pec_base()
	#pec_limit()
	#pec_limit_no_concentration()
	#photocatalytic_base()
	#photocatalytic_limit()
	#technology_comparison()
	#test()




	
if __name__ == '__main__':
	main()



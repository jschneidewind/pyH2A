from pyH2A.run_pyH2A import pyH2A
from pyH2A.Plugins import *
from tests.test_pyh2a import validate_dcf_insertions

def test_pve():
	results = pyH2A('./tests/PV_E.md', './tests/Results/PV_E/')
	expected_result = 4.194302976489678
	assert results.base_case.h2_cost == expected_result, f"Expected {expected_result} $/kg' but got {results.base_case.h2_cost} $/kg"
	
def test_pve_hourly_irradiation_plugin():
	"""Test the HourlyIrradiationPlugin with a sample DCF."""
	validate_dcf_insertions(HourlyIrradiationPlugin, 'PV_E/HourlyIrradiationPlugin')

def test_pve_photovoltaic_plugin():
	"""Test the PhotovoltaicPlugin with a sample DCF."""
	validate_dcf_insertions(PhotovoltaicPlugin, 'PV_E/PhotovoltaicPlugin')

def test_pve_electrolyzer_plugin():
	"""Test the ElectrolyzerPlugin with a sample DCF."""
	validate_dcf_insertions(ElectrolyzerPlugin, 'PV_E/ElectrolyzerPlugin')
    
def test_pve_battery_plugin():
	"""Test the BatteryPlugin with a sample DCF."""
	validate_dcf_insertions(BatteryPlugin, 'PV_E/BatteryPlugin')

def test_pve_stored_power_electrolysis_plugin():
	"""Test the StoredPowerElectrolysisPlugin with a sample DCF."""
	validate_dcf_insertions(StoredPowerElectrolysisPlugin, 'PV_E/StoredPowerElectrolysisPlugin')

def rest_pve_reverse_osmosis_plugin():
	"""Test the ReverseOsmosisPlugin with a sample DCF."""
	validate_dcf_insertions(ReverseOsmosisPlugin, 'PV_E/ReverseOsmosisPlugin')

def test_pve_power_management_plugin():
	"""Test the PowerManagementPlugin with a sample DCF."""
	validate_dcf_insertions(PowerManagementPlugin, 'PV_E/PowerManagementPlugin')

def test_pve_multiple_modules_plugin():
	"""Test the MultipleModulesPlugin with a sample DCF."""
	validate_dcf_insertions(MultipleModulesPlugin, 'PV_E/MultipleModulesPlugin')

def test_pve_capital_cost_plugin():
	"""Test the CapitalCostPlugin with a sample DCF."""
	validate_dcf_insertions(CapitalCostPlugin, 'PV_E/CapitalCostPlugin')
     
def test_pve_fixed_operating_cost_plugin():
	"""Test the FixedOperatingCostPlugin with a sample DCF."""
	validate_dcf_insertions(FixedOperatingCostPlugin, 'PV_E/FixedOperatingCostPlugin')

def test_pve_production_scaling_plugin():
	"""Test the ProductionScalingPlugin with a sample DCF."""
	validate_dcf_insertions(ProductionScalingPlugin, 'PEC/ProductionScalingPlugin')

def test_pve_replacement_plugin():
	"""Test the ReplacementPlugin with a sample DCF."""
	validate_dcf_insertions(ReplacementPlugin, 'PEC/ReplacementPlugin')
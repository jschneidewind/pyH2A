from pyH2A.run_pyH2A import pyH2A
from pyH2A.Plugins import *
from tests.test_pyh2a import validate_dcf_insertions

def test_pec():
	results = pyH2A('./tests/PEC.md', './tests/PEC/Base')
	expected_result = 139.41887561917213
	assert results.base_case.h2_cost == expected_result, f"Expected {expected_result} $/kg' but got {results.base_case.h2_cost} $/kg"
	
def test_pec_hourly_irradiation_plugin():
	"""Test the HourlyIrradiationPlugin with a sample DCF."""
	validate_dcf_insertions(HourlyIrradiationPlugin, 'PEC/HourlyIrradiationPlugin')

def rest_pec_reverse_osmosis_plugin():
	"""Test the ReverseOsmosisPlugin with a sample DCF."""
	validate_dcf_insertions(ReverseOsmosisPlugin, 'PEC/ReverseOsmosisPlugin')

def test_pec_multiple_modules_plugin():
	"""Test the MultipleModulesPlugin with a sample DCF."""
	validate_dcf_insertions(MultipleModulesPlugin, 'PEC/MultipleModulesPlugin')

def test_pec_capital_cost_plugin():
	"""Test the CapitalCostPlugin with a sample DCF."""
	validate_dcf_insertions(CapitalCostPlugin, 'PEC/CapitalCostPlugin')
     
def test_pec_fixed_operating_cost_plugin():
	"""Test the FixedOperatingCostPlugin with a sample DCF."""
	validate_dcf_insertions(FixedOperatingCostPlugin, 'PEC/FixedOperatingCostPlugin')

def test_pec_plugin():
	"""Test the PECPlugin with a sample DCF."""
	validate_dcf_insertions(PECPlugin, 'PEC/PECPlugin')

def test_pec_production_scaling_plugin():
	"""Test the ProductionScalingPlugin with a sample DCF."""
	validate_dcf_insertions(ProductionScalingPlugin, 'PEC/ProductionScalingPlugin')

def test_pec_replacement_plugin():
	"""Test the ReplacementPlugin with a sample DCF."""
	validate_dcf_insertions(ReplacementPlugin, 'PEC/ReplacementPlugin')

def test_pec_solar_concentrator_plugin():
	"""Test the SolarConcentratorPlugin with a sample DCF."""
	validate_dcf_insertions(SolarConcentratorPlugin, 'PEC/SolarConcentratorPlugin')

def test_pec_variable_operating_cost_plugin():
	"""Test the VariableOperatingCostPlugin with a sample DCF."""
	validate_dcf_insertions(VariableOperatingCostPlugin, 'PEC/VariableOperatingCostPlugin')
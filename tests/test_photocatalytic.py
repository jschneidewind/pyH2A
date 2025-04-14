from pyH2A.run_pyH2A import pyH2A
from pyH2A.Plugins import *
from tests.test_pyh2a import validate_dcf_insertions

def test_photocatalytic():
	results = pyH2A('./tests/Photocatalytic.md', './tests/Photocatalytic/Base')
	expected_result = 185.44329282256822
	assert results.base_case.h2_cost == expected_result, f"Expected {expected_result} $/kg' but got {results.base_case.h2_cost} $/kg"
	
def test_photocatalytic_hourly_irradiation_plugin():
	"""Test the HourlyIrradiationPlugin with a sample DCF."""
	validate_dcf_insertions(HourlyIrradiationPlugin, 'Photocatalytic/HourlyIrradiationPlugin')

def restphotocatalyticreverse_osmosis_plugin():
	"""Test the ReverseOsmosisPlugin with a sample DCF."""
	validate_dcf_insertions(ReverseOsmosisPlugin, 'Photocatalytic/ReverseOsmosisPlugin')

def test_photocatalytic_multiple_modules_plugin():
	"""Test the MultipleModulesPlugin with a sample DCF."""
	validate_dcf_insertions(MultipleModulesPlugin, 'Photocatalytic/MultipleModulesPlugin')

def test_photocatalytic_capital_cost_plugin():
	"""Test the CapitalCostPlugin with a sample DCF."""
	validate_dcf_insertions(CapitalCostPlugin, 'Photocatalytic/CapitalCostPlugin')
     
def test_photocatalytic_fixed_operating_cost_plugin():
	"""Test the FixedOperatingCostPlugin with a sample DCF."""
	validate_dcf_insertions(FixedOperatingCostPlugin, 'Photocatalytic/FixedOperatingCostPlugin')

def test_photocatalytic_plugin():
	"""Test the PhotocatalyticPlugin with a sample DCF."""
	validate_dcf_insertions(PhotocatalyticPlugin, 'Photocatalytic/PhotocatalyticPlugin')

def test_photocatalytic_production_scaling_plugin():
	"""Test the ProductionScalingPlugin with a sample DCF."""
	validate_dcf_insertions(ProductionScalingPlugin, 'Photocatalytic/ProductionScalingPlugin')

def test_photocatalytic_replacement_plugin():
	"""Test the ReplacementPlugin with a sample DCF."""
	validate_dcf_insertions(ReplacementPlugin, 'Photocatalytic/ReplacementPlugin')

def test_photocatalytic_variable_operating_cost_plugin():
	"""Test the VariableOperatingCostPlugin with a sample DCF."""
	validate_dcf_insertions(VariableOperatingCostPlugin, 'Photocatalytic/VariableOperatingCostPlugin')

def test_photocatalytic_catalyst_separation_plugin():
	"""Test the CatalystSeparationPlugin with a sample DCF."""
	validate_dcf_insertions(CatalystSeparationPlugin, 'Photocatalytic/CatalystSeparationPlugin')
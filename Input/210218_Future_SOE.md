# Workflow

Name | Type | Description
--- | --- | ---
Production_Scaling_Plugin | plugin | Computes plant output and scaling factors (if scaling is requested)
production_scaling | function | core function to process yearly plant output
Capital_Cost_Plugin | plugin | Calculation of direct, indirect and non-depreciable capital costs
initial_equity_depreciable_capital | function | core function to process depreciable capital costs
non_depreciable_capital_costs | function | core function to process non-depreciable capital costs
Replacement_Plugin | plugin | Calculation of replacement costs
replacement_costs | function | core function to process replacement costs
Fixed_Operating_Cost_Plugin | plugin | Calculation of fixed operating costs
fixed_operating_costs | function | core function to process fixed operating costs
Variable_Operating_Cost_Plugin | plugin | Calculation of variable operating costs, including utilities
variable_operating_costs | function | core function to process variable operating costs

# Technical Operating Parameters and Specifications

Name | Value | Path | Full Name
--- | --- | --- | --
Operating Capacity Factor (%) | 87.5%
Plant Design Capacity (kg of H2/day) | 50,000

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2040
basis year | Basis year | 2012
current year capital costs | Current year for capital costs | 2010
startup time | Start-up Time (years) | 1
plant life | Plant life (years) | 40
analysis period | Analysis period (years) | 40
depreciation length | Depreciation Schedule Length (years) | 20
depreciation type | Depreciation Type | MACRS
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%
debt | Debt period | Constant
startup cost fixed | % of Fixed Operating Costs During Start-up | 100%
startup revenues | % of Revenues During Start-up | 50%
startup cost variable | % of Variable Operating Costs During Start-up | 75%
decommissioning | Decommissioning costs (% of depreciable captical investment) | 10%
salvage | Salvage value (% of total capitcal investment) | 10%
inflation | Inflation rate (%) | 1.9%
irr | After-tax Real IRR (%) | 8.0%
state tax | State Taxes (%) | 6.0%
federal tax | Federal Taxes (%) | 21.0%
working capital | Working Capital (% of yearly change in operating costs) | 15.0%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# Direct Capital Costs

Name | Full Name | Value | Path
--- | --- | --- | ---
Electrolyzer Stack | Cost calculated based on output ($/kg of H2/day) | 144.64125 | Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value 
Electrolyzer BoP | Cost calculated based on output ($/kg of H2/day) | 484.23375 | Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value 

# Direct Capital Costs - Installation

Name | Value | Path
--- | --- | ---
Stack installation (% of stack cost) | 10% | Direct Capital Costs > Electrolyzer Stack > Value
BoP installation (% of BoP cost) | 10% | Direct Capital Costs > Electrolyzer BoP > Value

# Indirect Capital Costs

Name | Value | Path
--- | --- | ---
Site Preparation (% of direct capital costs) | 2% | Direct Capital Costs > Total > Value
Engineering and Design (% of direct capital costs) | 10% | Direct Capital Costs > Total > Value
Process Contingency (% of direct capital costs) | 7.1741% | Direct Capital Costs > Total > Value
Project Contingency (% of direct capital costs) | 7.1741% | Direct Capital Costs > Total > Value
Up-Front Permitting Costs (% of direct capital costs) | 15% | Direct Capital Costs > Total > Value

# Non-Depreciable Capital Costs

Name | Value
--- | ---
Cost of land ($ per acre) | 50,000.0
Land required (acres) | 5

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Total plant staff (FTEs) | 15
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Value | Path
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | 20.0% | Fixed Operating Costs > Labor Cost - Uninflated > Value
property tax | Property tax and insurance rate (% of total capital investment per year) | 2.0% | Total Capital Costs > Total > Value
repair | Production Maintenance and Repairs (% of direct capital costs) | 3% | Direct Capital Costs > Total > Value

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | ---
Industrial Natural Gas | 0.04579 | mmBTU/kg H2 | ../Lookup_Tables/Industrial_Natural_Gas_AEO_2017_Reference_Case.csv | mmBTU | 1.055 | GJ/mmBTU
Industrial Electricity | 35.1 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 2.378 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

# Planned Replacement

Name | Frequency (years) | Cost ($) | Path
--- | --- | --- | ---
Annual Replacement (% of direct capital costs) | 1 | 2.9486% | Direct Capital Costs > Total > Value
BoP Replacement (% of direct capital costs | 20 | 77% | Direct Capital Costs > Total > Value

# Unplanned Replacement

Name | Full Name | Value | Path
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | 0.5% | Depreciable Capital Costs > Inflated > Value

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Utilities > Industrial Electricity > Usage per kg H2 | Electricity Usage (kWh/kg H2) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H2/day) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | factor | 95%; 105%
Financial Input Values > irr > Value | Internal Rate of Return | factor | 95%; 105%
Utilities > Process Water > Usage per kg H2 | Water Usage per kg H2 | factor | 50%; 150%
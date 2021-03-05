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
Operating Capacity Factor (%) | 90%
Plant Design Capacity (kg of H2/day) | 379,387.0
New Plant Design Capacity (kg of H2/day) | 379,387.0
Capital Scaling Exponent | 0.6

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2015
basis year | Basis year | 2005
current year capital costs | Current year for capital costs | 2010
startup time | Start-up Time (years) | 1
plant life | Plant life (years) | 40
analysis period | Analysis period (years) | 40
depreciation length | Depreciation Schedule Length (years) | 20
depreciation type | Depreciation Type | MACRS
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%
debt | Debt period | Constant
startup cost fixed | % of Fixed Operating Costs During Start-up | 75%
startup revenues | % of Revenues During Start-up | 50%
startup cost variable | % of Variable Operating Costs During Start-up | 75%
decommissioning | Decommissioning costs (% of depreciable captical investment) | 10%
salvage | Salvage value (% of total capitcal investment) | 10%
inflation | Inflation rate (%) | 1.9%
irr | After-tax Real IRR (%) | 8.0%
state tax | State Taxes (%) | 6.0%
federal tax | Federal Taxes (%) | 21.0%
working capital | Working Capital (% of yearly change in operating costs) | 15.0%
Sensitivity Factor | Factor for sensitivity of capital costs | 1.

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 8%
capital perc 2nd | % of Capital Spent in 2nd Year of Construction | 60%
capital perc 3rd | % of Capital Spent in 3rd Year of Construction | 32%

# Direct Capital Costs

Name | Value | Path
--- | --- | ---
Process Plant Equipment ($) | 49,969,788.0 | Financial Input Values > Sensitivity Factor > Value ; Scaling > Capital Scaling Factor > Value
Balance of Plant and Offsites ($) | 19,964,651.0 | Financial Input Values > Sensitivity Factor > Value ; Scaling > Capital Scaling Factor > Value
SCR NOx Control on Stack ($) | 296,651.0 | Financial Input Values > Sensitivity Factor > Value ; Scaling > Capital Scaling Factor > Value

# Direct Capital Costs - Installation

Name | Value | Path
--- | --- | ---
Installation Costs (% of capital costs) | 92% | Direct Capital Costs > Summed Total > Value

# Indirect Capital Costs

Name | Value | Path
--- | --- | ---
Site Preparation (% of direct capital costs) | 2% | Direct Capital Costs > Total > Value
Engineering and Design (% of direct capital costs) | 10% | Direct Capital Costs > Total > Value 
Project Contigency Reactors and Compressors (% of direct capital costs ) | 15% | Direct Capital Costs > Total > Value
Up-Front Permitting Costs (% of direct capital costs) | 15% | Direct Capital Costs > Total > Value

# Non-Depreciable Capital Costs

Name | Value
--- | ---
Cost of land ($ per acre) | 50,000.0
Land required (acres) | 10.0

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Total plant staff (FTEs) | 20
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Value | Path
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | 20.0% | Fixed Operating Costs > Labor Cost - Uninflated > Value
property tax | Property tax and insurance rate (% of total capital investment per year) | 2.0% | Total Capital Costs > Total > Value
repairs | Material Cost for Repairs ($) | 810,097.0

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | ---
Industrial Natural Gas | 0.15625 | mmBTU/kg H2 | ../Lookup_Tables/Industrial_Natural_Gas_AEO_2017_Reference_Case.csv | mmBTU | 1.055 | GJ/mmBTU
Industrial Electricity | 0.569 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | kWh | 0.0036 | GJ/kWh
Demineralized Water | 3.355 | gal/kg H2 | 0.007124853 | $(2016)/gal | 1. | None
Cooling Water | 1.495 | gal/kg H2 | 0.00011335 | $(2016)/gal | 1. | None

# Other Variable Operating Costs

Name | Value
--- | ---
Surcharge ($/year) | 2,123,000.0

# Unplanned Replacement

Name | Full Name | Value | Path
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | 0.5% | Depreciable Capital Costs > Inflated > Value

# Planned Replacement

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Utilities > Industrial Natural Gas > Usage per kg H2 | Natural Gas Consumption | factor | 95%; 105%
Technical Operating Parameters and Specifications > New Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H_{2}/day) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | factor | 95%; 105%
Financial Input Values > irr > Value | Internal Rate of Return | factor | 95%; 105%
Utilities > Demineralized Water > Usage per kg H2 | Water Usage per kg H_{2} | factor | 95%; 105%
Financial Input Values > Sensitivity Factor > Value | Capital Costs | factor | 95%; 105%
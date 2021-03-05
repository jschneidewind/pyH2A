# Workflow

Name | Type | Description
--- | --- | ---
Production_Scaling_Plugin | plugin | Computes plant output and scaling factors (if scaling is requested)
production_scaling | function | core function to process yearly plant output
Solar_Thermal_Plugin | plugin | Computes required land area based on STH and solar input
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
Plant Design Capacity (kg of H2/day) | 100,000

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2040
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

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 8%
capital perc 2nd | % of Capital Spent in 2nd Year of Construction | 60%
capital perc 3rd | % of Capital Spent in 3rd Year of Construction | 32%

# Solar-to-Hydrogen Efficiency

Name | Value
--- | ---
STH (%) | 20%

# Solar Input

Name | Value
--- | ---
Mean solar input (kWh/m2/day) | 5.266

# Direct Capital Costs - Reactors and Compression System

Name | Value | Path
--- | --- | ---
ZrO2 ($) | 39,079.0
Ferrite ($) | 39,384,465.0
Compression System ($) | 28,275,885.0
Solar Reactors ($) | 21,509,152.0
Vacuum Pumps ($) | 3,745,422.0
Water Pumps ($) | 75,514.0
Turbine ($) | 535,343.0
Heat Exchangers ($) | 291,974.0
Solar Reactor Installation (% of solar reactor cost) | 217% | Direct Capital Costs - Reactors and Compression System > Solar Reactors ($) > Value
Vacuum Pumps Installation (% of vacuum pump cost) | 230% | Direct Capital Costs - Reactors and Compression System > Vacuum Pumps ($) > Value
Water Pumps Installation (% of water pump cost) | 230% | Direct Capital Costs - Reactors and Compression System > Water Pumps ($) > Value
Turbine Installation (% of turbine cost) | 115% | Direct Capital Costs - Reactors and Compression System > Turbine ($) > Value
Heater Exchanger Installation (% of heat exchanger cost) | 217% | Direct Capital Costs - Reactors and Compression System > Heat Exchangers ($) > Value

# Direct Capital Costs - Heliostat

Name | Value
--- | ---
Heliostats ($) | 149,303,193.0
Secondary Concentrators ($) | 570,585.0
Towers ($) | 56,366,861.0

# Indirect Capital Costs

Name | Value | Path
--- | --- | ---
Site Preparation (% of direct capital costs) | 2% | Direct Capital Costs > Total > Value
Engineering and Design (% of heliostat cost) | 17.8% | Direct Capital Costs - Heliostat > Summed Total > Value
Project Contingency Heliostat (% of heliostat cost) | 16.8% | Direct Capital Costs - Heliostat > Summed Total > Value
Project Contigency Reactors and Compressors (% of reactors and compressors cost) | 18% | Direct Capital Costs - Reactors and Compression System > Summed Total > Value
Up-Front Permitting Costs (% of direct capital costs) | 7.5% | Direct Capital Costs > Total > Value

# Non-Depreciable Capital Costs

Name | Value
--- | ---
Cost of land ($ per acre) | 5000.0
Additional Land Area (%) | 0%

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Total plant staff (FTEs) | 47.7
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 33.53

# Other Fixed Operating Costs

Name | Full Name | Value | Path
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | 20.0% | Fixed Operating Costs > Labor Cost - Uninflated > Value
heliostat insurance | % of heliostat cost | 1% | Direct Capital Costs - Heliostat > Summed Total > Value
reactor and compression insurance | % of reactor and compression cost | 2% | Direct Capital Costs - Reactors and Compression System > Summed Total > Value
heliostat repairs | % of heliostat cost | 0.5% | Direct Capital Costs - Heliostat > Summed Total > Value
reactor and compression repairs | % of reactor and compression cost | 6% | Direct Capital Costs - Reactors and Compression System > Summed Total > Value
Permits ($/year) | Permits, Licensing | 1,000.0

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 2.01 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 2.378 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

# Other Variable Operating Costs

Name | Value
--- | ---
Surcharge ($/year) | 2,123,000.0

# Planned Replacement

Name | Frequency (years) | Cost ($) | Path
--- | --- | --- | ---
ZrO2 Replacement (% of ZrO2 cost) | 5 | 100% | Direct Capital Costs - Reactors and Compression System > ZrO2 ($) > Value
Ferrite Replacement (% of Ferrite Cost) | 5 | 100% | Direct Capital Costs - Reactors and Compression System > Ferrite ($) > Value

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
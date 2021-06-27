# Workflow

Name | Type | Description | Position
--- | --- | --- | ---
Production_Scaling_Plugin | plugin | Computes plant output and scaling factors (if scaling is requested)
production_scaling | function | core function to process yearly plant output
Photocatalytic_Plugin | plugin | Computes number of required baggies, cost of baggies and catalyst cost | 2
Capital_Cost_Plugin | plugin | Calculation of direct, indirect and non-depreciable capital costs
Multiple_Modules_Plugin | plugin | Modelling of module plant modules, adjustment of labor requirement | 3
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
--- | --- | --- | ---
Operating Capacity Factor (%) | 90.0%
Plant Design Capacity (kg of H2/day) | 1,111
Maximum Output at Gate | 90.00900090009% | Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | % of plant design capacity
Scaling Ratio | 1.
Plant Modules | 10

# Financial Input Values

Name | Full Name | Value | Path
--- | --- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2040
basis year | Basis year | 2005
current year capital costs | Current year for capital costs | 2005
startup time | Start-up Time (years) | 1
plant life | Plant life (years) | 20
analysis period | Analysis period (years) | 20
depreciation length | Depreciation Schedule Length (years) | 20
depreciation type | Depreciation Type | MACRS
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%
debt | Debt period | Constant
startup cost fixed | % of Fixed Operating Costs During Start-up | 100%
startup revenues | % of Revenues During Start-up | 75%
startup cost variable | % of Variable Operating Costs During Start-up | 75%
decommissioning | Decommissioning costs (% of depreciable captical investment) | 10%
salvage | Salvage value (% of total capital investment) | 10%
inflation | Inflation rate (%) | 1.9%
irr | After-tax Real IRR (%) | 8.0%
state tax | State Taxes (%) | 6.0%
federal tax | Federal Taxes (%) | 21.0%
working capital | Working Capital (% of yearly change in operating costs) | 15.0%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# Catalyst

Name | Value
--- | ---
Cost per kg ($) | 304.0
Concentration (kg/L) | 0.00001052
Lifetime (years) | 5

# Reactor Baggies

Name | Value
--- | ---
Cost Material Top ($/m2) | 0.54
Cost Material Bottom ($/m2) | 0.47
Number of ports | 12
Cost of port ($) | 30
Other Costs ($) | 610.7
Markup factor | 1.5
Length (m) | 323.0
Width (m) | 12.2
Height (m) | 0.1
Additional land area (%) | 30.0%
Lifetime (years) | 5

# Direct Capital Costs

Name | Value
--- | ---
Baggie roll system ($) | 37,000.0
Forklift ($) | 18,571.0
Water pump ($) | 213.0
Water pipes ($) | 718.0

# Direct Capital Costs - Gas Processing

Name | Value | Path
--- | --- | ---
Compressor ($) | 526,302.0
Condenser ($) | 13,765.0
Intercooler-1 ($) | 15,103.0
Intercooler-2 ($) | 15,552.0
Pressure Swing Adsorption ($) | 107,147.0
Piping ($) | 6416.0

# Direct Capital Costs - Control System

Name | Path | Value
--- | --- | ---
PLC ($) | None | 2,000.0
Control Room Building ($) | None | 8,000.0
Control Room Wiring Panel ($) | None | 3,000.0
Bed Wiring Panel (cost per baggie) | Reactor Baggies > Number > Value | 146.0
Computer and Monitor ($) | None | 1,500.0
Labview Software ($) | None | 4,299.0
Water Level Controllers (cost per baggie) | Reactor Baggies > Number > Value | 50.0
Pressure Sensors (cost per baggie) | Reactor Baggies > Number > Value | 345.0
Hydrogen Area Sensors (cost per baggie) | Reactor Baggies > Number > Value | 7,600.0
Gas Flow Meter ($) | None | 5,500.0
Instrument Wiring ($) | None | 409.0
Power Wiring ($) | None | 136.0
Conduit ($) | None | 2,563.0

# Direct Capital Costs - Installation Costs

Name | Path | Value
--- | --- | ---
Excavation ($) | None | 46,259.0
Baggie Reactor Startup ($) | None | 7134.0
Baggies installation (cost per baggie) | Reactor Baggies > Number > Value | 800.0
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 30%
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 30%

# Indirect Capital Costs

Name | Path | Value
--- | --- | ---
Engineering and Design (% of total direct capital costs)| Direct Capital Costs > Total > Value  | 7%
Process Contingency (% of total direct capital costs) | Direct Capital Costs > Total > Value | 20.0%
Project Contingency ($) | None | 0.0
Other (Depreciable) Capital ($) | None | 0.0
Up-Front Permitting Costs (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
Site Preparation (% of total direct capital costs) | Direct Capital Costs > Total > Value | 1%

# Non-Depreciable Capital Costs

Name | Value | Path
--- | --- | ---
Cost of land ($ per acre) | 500.0 

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
area | Area per staff (m2) | 405,000
supervisor | Shift supervisor | 1
shifts | Shifts | 3
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Path | Value
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 20.0%
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 2.0%
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
rent | Rent ($ per year) | None | 0.0
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0
material cost repair | Material costs for maintenance and repairs ($ per year) | None | 0.0
other fees | Other Fees ($ per year) | None | 0.0
other o&m | Other Fixed O&M Costs ($ per year) | None | 0.0

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Path | Usage Path
--- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 3.29 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 2.637 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

# Other Variable Operating Costs

Name | Full Name | Value
--- | --- | ---
other | Other Variable Operating Costs ($/year) | 0.0
material | Other Material Costs ($/year) | 0.0
waste | Waste Treatment Costs ($/year) | 0.0
solid waste | Solid waste disposal costs ($/year) | 0.0
royalties | Royalties ($/year) | 0.0
profit | Operator Profit ($/year) | 0.0
subsidies | Subsidies, Tax Incentives ($/year) | 0.0

# Unplanned Replacement

Name | Full Name | Path | Value
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.5%

# Solar-to-Hydrogen Efficiency

Name | Value
--- | ---
STH (%) | 10.0%

# Solar Input

Name | Value
--- | ---
Mean solar input (kWh/m2/day) | 5.25

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H_{2}/day) | value | 1200; 950
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | value | 86%; 95%
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 5%; 15%
Catalyst > Cost per kg ($) > Value | Catalyst Cost | factor | 0.1; 20
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 0.3; 10 
Other Fixed Operating Costs > repairs > Value | Repair Costs | factor | 70%; 130%
Solar Input > Mean solar input (kWh/m2/day) > Value | Solar Input | factor | 70%; 120%

# Waterfall Analysis Old

Parameter | Name | Type | Value
--- | --- | --- | ---
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Design Capacity (kg $H_{2}$/day) | value | 1200
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | value | 86%
Catalyst > Cost per kg ($) > Value | Catalyst Cost ($/kg) | factor | 0.1
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 1
Other Fixed Operating Costs > repairs > Value | Repair Costs | factor | 70%
Solar Input > Mean solar input (kWh/m2/day) > Value | Solar Input (kWh/$m^{2}$/ day) | factor | 70%
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 5%

# Waterfall Analysis

Parameter | Name | Type | Value | Show Percent
--- | --- | --- | --- | ---
Catalyst > Cost per kg ($) > Value | Catalyst Cost ($/kg) | value | 6,000.0
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 2% | True
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 0.1
Catalyst > Concentration (kg/L) > Value | Catalyst Concentration (kg/L) | factor | 0.1

# Monte Carlo Analysis - Parameters

Parameter | Name | Type | Values
--- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 20%; 2%
Catalyst > Cost per kg ($) > Value | Catalyst Cost | value | 100.0; 6000.0
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 0.1; 10
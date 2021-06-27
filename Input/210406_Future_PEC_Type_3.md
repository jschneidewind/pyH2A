Financial parameter differences: 100% equity, 10% IRR, 35% federal tax, 

# Workflow

Name | Type | Description | Position
--- | --- | --- | ---
Production_Scaling_Plugin | plugin | Computes plant output and scaling factors (if scaling is requested)
production_scaling | function | core function to process yearly plant output
PEC_Plugin | plugin | PEC Plugin | 2
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
Plant Design Capacity (kg of H2/day) | 1,000
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

# PEC Cells

Name | Value
--- | ---
Cell Cost ($/m2)| 153.0
Lifetime (years) | 10
Length (m) | 2
Width (m) | 1

# Land Area Requirement

Name | Value
--- | ---
Cell Angle (degree) | 35
South Spacing (m) | 6.5
East/West Spacing (m) | 0.1

# Direct Capital Costs - Water Management

Name | Value | Path
--- | --- | ---
Water pump ($) | 213.0
Water Manifold Piping ($ per cell) | 1.693 | PEC Cells > Number > Value
Water Collection Piping ($ per cell) | 1.969 | PEC Cells > Number > Value
Water Column Collection Piping ($ per cell) | 0.2467 | PEC Cells > Number > Value
Water Final Collection Piping ($ per cell) | 0.032 | PEC Cells > Number > Value

# Direct Capital Costs - Gas Processing

Name | Value | Path
--- | --- | ---
Compressor ($) | 759,481.0
Condenser ($) | 16,607.0
Intercooler-1 ($) | 17,894.0
Intercooler-2 ($) | 18,495.0
Manifold Piping ($ per cell) | 1.693 | PEC Cells > Number > Value
Collection Piping ($ per cell) | 1.969 | PEC Cells > Number > Value
Column Collection Piping ($ per cell) | 0.2467 | PEC Cells > Number > Value
Final Collection Piping ($ per cell) | 0.032 | PEC Cells > Number > Value

# Direct Capital Costs - Control System

Name | Path | Value
--- | --- | ---
PLC ($) | None | 3,000.0
Control Room Building ($) | None | 17,527.0
Control Room Wiring Panel ($) | None | 3,000.0
Computer and Monitor ($) | None | 1,500.0
Labview Software ($) | None | 4,299.0
Water Level Controllers (cost per cell, $) | PEC Cells > Number > Value | 5.0
Pressure Sensors (cost per cell, $) | PEC Cells > Number > Value | 0.2334
Hydrogen Area Sensors (cost per cell, $) | PEC Cells > Number > Value | 5.1415
Hydrogen Flow Meter ($) | None | 5,500.0
Instrument Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.017
Power Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.008456
Conduit (cost per cell, $) | PEC Cells > Number > Value | 0.253

# Direct Capital Costs - Installation Costs

Name | Path | Value
--- | --- | ---
Piping Installation (per cell, $) | PEC Cells > Number > Value | 1.16
Cell Installation (per m2 of cell area) | Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value | 20.0
Pump Installation (% of pump cost) | Direct Capital Costs - Water Management > Water pump ($) > Value | 30%
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 30%
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 30%

# Indirect Capital Costs

Name | Path | Value
--- | --- | ---
Engineering and Design (% of total direct capital costs)| Direct Capital Costs > Total > Value  | 7%
Process Contingency (% of total direct capital costs) | Direct Capital Costs > Total > Value | 20.0%
Up-Front Permitting Costs (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
Site Preparation (% of total direct capital costs) | Direct Capital Costs > Total > Value | 1%

# Non-Depreciable Capital Costs

Name | Value | Path
--- | --- | ---
Cost of land ($ per acre) | 500.0 

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
area | Area per staff (m2) | 100,000
supervisor | Shift supervisor | 1
shifts | Shifts | 3
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Path | Value
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 20.0%
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 2.0%
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Path | Usage Path
--- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 2.00 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 2.369 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

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
Mean solar input (kWh/m2/day) | 6.19

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 5%; 20%
PEC Cells > Cell Cost ($/m2) > Value | PEC Cell Cost (USD/m^{2}) | value | 80.0; 200.0
PEC Cells > Lifetime (years) > Value | PEC Cell Lifetime (years) | value | 5; 20
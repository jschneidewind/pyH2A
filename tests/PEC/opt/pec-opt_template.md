# Workflow

Parameter | Type | Position | Description
--- | --- | --- | ---
[...] | plugin, optional | int, optional | n/a
Energy.HourlyIrradiationPlugin | plugin | 0 | Plugin to calculate solar irradiation from typical meteorological year data
Hydrogen.PECPlugin | plugin | 2 | Plugin to model photoelectrochemical water splitting
Energy.SolarConcentratorPlugin | plugin | 2 | Plugin to model solar concentration
Background.MultipleModulesPlugin | plugin | 3 | Modelling of module plant modules, adjustment of labor requirement

# Construction

Parameter | Value | Full Name
--- | --- | ---
[...] | float | n/a
capital perc 1st | 1.0 | % of Capital Spent in 1st Year of Construction

# Technical Operating Parameters and Specifications

Parameter | Value
--- | ---
Maximum Output at Gate | float, optional
New Plant Design Capacity (kg of H2/day) | float, optional
Scaling Ratio | float, optional
Capital Scaling Exponent | float, optional
Labor Scaling Exponent | float, optional
Operating Capacity Factor (%) | 0.9
Plant Design Capacity (kg of H2/day) | 1000
Plant Modules | 10

# PEC Cells

Parameter | Value | Comment
--- | --- | ---
Lifetime (year) | float | n/a
Cell Cost ($/m2) | 21000.0 | # price of III-V solar cells as reference, approximate $/W to $/m2 conversion formula: Cost ($/W) * conversion_efficiency (%) * 1000 W/m2 = Cost ($/m2), Reference: Horowitz 2018 (NREL), 70 $/W, assuming 30% efficiency = 21,000 $/m2
Lifetime (years) | 0.3 | # should consider operational lifetime (irradiation for only 8 h per day), baseline 1000 h operation time (reference: Kistler 2020), 3000 h total, 0.3 years
Length (m) | 6 | n/a
Width (m) | 0.3 | n/a

# [...] Direct Capital Cost [...]

Parameter | Value
--- | ---
[...] | float

# [...] Indirect Capital Cost [...]

Parameter | Value
--- | ---
[...] | float

# [...] Other Non-Depreciable Capital Cost [...]

Parameter | Value
--- | ---
[...] | float

# Planned Replacement

Parameter | Frequency (years) | Cost ($)
--- | --- | ---
[...] | float | float

# [...] Unplanned Replacement [...]

Parameter | Value
--- | ---
[...] | float

# [...] Other Fixed Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Utilities

Parameter | Cost | Usage per kg H2 | Price Conversion Factor | Path | Usage Path | Usage Unit | Cost Unit | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | --- | --- | ---
[...] | float, ndarray or str | float | float | str, optional | str, optional | n/a | n/a | n/a
Industrial Electricity | pyH2A.Lookup_Tables.Utility_Cost~Industrial_Electricity_AEO_2017_Reference_Case.csv | 0.16 | 0.0036 | n/a | n/a | kWh/kg H2 | GJ | GJ/kWh
Process Water | 0.0023749510945008 | 2.369 | 1.0 | n/a | n/a | gal/kg H2 | $(2016)/gal | None

# [...] Other Variable Operating Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# SensitivityAnalysis

Parameter | Name | Type | Values
--- | --- | --- | ---
[...] | str | str | str
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 10%; 25%
PEC Cells > Cell Cost ($/m2) > Value | PEC Cell Cost (USD/m^{2}) | value | 200.0; 450.0
PEC Cells > Lifetime (years) > Value | PEC Cell Lifetime (years) | value | 5; 20

# MonteCarloAnalysis

Parameter | Value
--- | ---
Output File | str, optional
Samples | 1000
Target Price Range ($) | 1.5; 2.5
Input File | pyH2A.Example~Future_PEC_Type_4_Monte_Carlo.csv

# Parameters - MonteCarloAnalysis

Parameter | Name | Type | Values | File Index
--- | --- | --- | --- | ---
[...] | str | str | str | int, optional
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | Base; 30% | 0
PEC Cells > Cell Cost ($/m2) > Value | \$ / $m^{2}$(PEC Cell) | value | 100.0; Base | 1
PEC Cells > Lifetime (years) > Value | Cell Lifetime / years | value | Base; 3 | 2
Solar Concentrator > Cost ($/m2) > Value | \$ / $m^{2}$(Solar Concentrator) | value | 60; Base | 3

# Display Parameters

Parameter | Value
--- | ---
Name | PEC Type 4
Color | darkred

# Financial Input Values

Parameter | Full Name | Value
--- | --- | ---
basis year | Basis year | 2005
current year capital costs | Current year for capital costs | 2005
equity | % Equity Financing | 0.4
interest | Interest rate on debt (%) | 0.037000000000000005

# Hourly Irradiation

Parameter | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Dagget, CA, USA

# Irradiance Area Parameters

Parameter | Value | Comment
--- | --- | ---
Module Tilt (degrees) | 0 | n/a
Array Azimuth (degrees) | 0 | n/a
Nominal Operating Temperature (Celsius) | 45 | n/a
Mismatch Derating | 0.98 | n/a
Dirt Derating | 0.98 | Values taken from Chang 2020, analogues to silicon PV
Temperature Coefficient (per Celsius) | 0.0 | n/a

# Solar Input

Parameter | Value | Path | Comment
--- | --- | --- | ---
Mean solar input (kWh/m2/day) | Hourly Irradiation > Mean solar input two axis tracking (kWh/m2/day) > Value | Solar Concentrator > Concentration Factor > Value | Two axis tracking irradiation from hourly irradiation multiplied by solar concentration factor to give solar input incident on PEC cells

# Solar-to-Hydrogen Efficiency

Parameter | Value | Comment
--- | --- | ---
STH (%) | 0.14 | # Reference Kistler 2020 (Note: vapor-fed device used in reference, techno-economic analysis assumes liquid phase design)

# Solar Concentrator

Parameter | Value | Comment
--- | --- | ---
Concentration Factor | 50 | Concentration factor increased from 10 (Pinaud 2013) to 50 due to high PEC cell cost
Cost ($/m2) | 100 | Taken from Pinaud 2013

# Land Area Requirement

Parameter | Value
--- | ---
Cell Angle (degree) | 35
South Spacing (m) | 6.71
East/West Spacing (m) | 17.3

# Direct Capital Costs - Water Management

Parameter | Value | Path
--- | --- | ---
Water pump ($) | 213.0 | n/a
Water Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value
Water Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value
Water Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value
Water Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value

# Direct Capital Costs - Gas Processing

Parameter | Value | Path
--- | --- | ---
Condenser ($) | 7098.0 | n/a
Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value
Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value
Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value
Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value

# Direct Capital Costs - Control System

Parameter | Path | Value
--- | --- | ---
PLC ($) | None | 3000.0
Control Room Building ($) | None | 17527.0
Control Room Wiring Panel ($) | None | 3000.0
Computer and Monitor ($) | None | 1500.0
Labview Software ($) | None | 4299.0
Water Level Controllers (cost per cell, $) | PEC Cells > Number > Value | 50.0
Pressure Sensors (cost per cell, $) | PEC Cells > Number > Value | 3.333
Hydrogen Area Sensors (cost per cell, $) | PEC Cells > Number > Value | 73.42
Hydrogen Flow Meter ($) | None | 5500.0
Instrument Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.252
Power Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.1256
Conduit (cost per cell, $) | PEC Cells > Number > Value | 3.759

# Direct Capital Costs - Installation Costs

Parameter | Path | Value
--- | --- | ---
Piping Installation (per cell, $) | PEC Cells > Number > Value | 5.65
Reactor Installation (per m2 of solar collection area) | Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value | 22.0
Pump Installation (% of pump cost) | Direct Capital Costs - Water Management > Water pump ($) > Value | 0.3
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 0.3
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 0.3

# Indirect Capital Costs

Parameter | Path | Value
--- | --- | ---
Engineering and Design (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.07
Process Contingency (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.2
Up-Front Permitting Costs (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.005
Site Preparation (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.01

# Non-Depreciable Capital Costs

Parameter | Value
--- | ---
Cost of land ($ per acre) | 500.0

# Fixed Operating Costs

Parameter | Full Name | Value
--- | --- | ---
area | Area per staff (m2) | 60000
supervisor | Shift supervisor | 1
shifts | Shifts | 3
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Parameter | Full Name | Path | Value
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 0.2
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 0.02
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.005
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0

# Unplanned Replacement

Parameter | Full Name | Path | Value
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.005

# Methods - MonteCarloAnalysis

Parameter | Method Name | Arguments
--- | --- | ---
distance_histogram | plot_distance_histogram | {'show': False}
distance_cost_relationship | plot_distance_cost_relationship | {'show': False}


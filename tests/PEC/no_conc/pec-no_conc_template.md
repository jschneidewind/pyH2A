# Workflow

Parameter | Type | Position | Description
--- | --- | --- | ---
[...] | plugin, optional | int, optional | n/a
Energy.HourlyIrradiationPlugin | plugin | 0 | Plugin to calculate solar irradiation from typical meteorological year data
Hydrogen.PECPlugin | plugin | 2 | Plugin to model photoelectrochemical water splitting
Background.MultipleModulesPlugin | plugin | 3 | Modelling of module plant modules, adjustment of labor requirement

# Construction

Parameter | Value | Full Name
--- | --- | ---
[...] | float | n/a
capital perc 1st | 1.0 | % of Capital Spent in 1st Year of Construction

# Technical Operating Parameters and Specifications

Parameter | Value | Path | Full Name
--- | --- | --- | ---
Maximum Output at Gate | float, optional | n/a | n/a
New Plant Design Capacity (kg of H2/day) | float, optional | n/a | n/a
Scaling Ratio | float, optional | n/a | n/a
Capital Scaling Exponent | float, optional | n/a | n/a
Labor Scaling Exponent | float, optional | n/a | n/a
Operating Capacity Factor (%) | 0.9 | n/a | n/a
Plant Design Capacity (kg of H2/day) | 1000 | n/a | n/a
Plant Modules | 10 | None | 10 identical modules, only affects labor requirement calculation.

# PEC Cells

Parameter | Value | Comment
--- | --- | ---
Lifetime (year) | float | n/a
Cell Cost ($/m2) | 700.0 | Price of III-V solar cells as reference, approximate $/W to $/m2 conversion formula: Cost ($/W) * conversion_efficiency (%) * 1000 W/m2 = Cost ($/m2), Reference: Horowitz 2018 (NREL), 70 $/W, assuming 30% efficiency = 21,000 $/m2. 30-fold cost reduction analogous to 30-fold cost reduction for photocatalyst in photocatalytic model.
Lifetime (years) | 3.0 | 9-fold lifetime increase relative to base case (0.33 years).
Length (m) | 6 | Based on sizing in Pinaud 2013.
Width (m) | 0.3 | Based on sizing in Pinaud 2013.

# Solar Concentrator

Parameter | Value
--- | ---
Concentration Factor | float, optional

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

Parameter | Cost | Usage per kg H2 | Price Conversion Factor | Path | Usage Path | Usage Unit | Cost Unit | Price Conversion Factor Unit | Comment
--- | --- | --- | --- | --- | --- | --- | --- | --- | ---
[...] | float, ndarray or str | float | float | str, optional | str, optional | n/a | n/a | n/a | n/a
Industrial Electricity | pyH2A.Lookup_Tables.Utility_Cost~Industrial_Electricity_AEO_2017_Reference_Case.csv | 0.16 | 0.0036 | n/a | n/a | kWh/kg H2 | GJ | GJ/kWh | Electricity usage based on Pinaud 2013.
Process Water | 0.0023749510945008 | 2.369 | 1.0 | n/a | n/a | gal/kg H2 | $(2016)/gal | None | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to ca. 0.0023 $/gal), based on Kibria 2021 and Driess 2021.

# [...] Other Variable Operating Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# SensitivityAnalysis

Parameter | Name | Type | Values
--- | --- | --- | ---
[...] | str | str | str
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH efficiency | value | 15%; 40%
PEC Cells > Cell Cost ($/m2) > Value | PEC cell cost (\$/m^{2}) | value | 350; 1,400
PEC Cells > Lifetime (years) > Value | PEC cell lifetime (years) | value | 1.5; 6

# Display Parameters

Parameter | Value
--- | ---
Name | PEC Type 3
Color | darkred

# Hourly Irradiation

Parameter | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Location: Dagget, CA, USA

# Irradiance Area Parameters

Parameter | Value | Comment
--- | --- | ---
Module Tilt (degrees) | 0 | Two axis tracking, module tilt and array azimuth change are not relevant.
Array Azimuth (degrees) | 0 | n/a
Nominal Operating Temperature (Celsius) | 45 | Temperature is stabilized by intrinsic water cooling.
Mismatch Derating | 0.98 | n/a
Dirt Derating | 0.98 | Values taken from Chang 2020, analogues to silicon PV
Temperature Coefficient (per Celsius) | 0.0 | No assumed efficiency loss with higher temperature.

# Solar Input

Parameter | Value | Path | Comment
--- | --- | --- | ---
Mean solar input (kWh/m2/day) | Hourly Irradiation > Mean solar input two axis tracking (kWh/m2/day) > Value | None | Two axis tracking irradiation from hourly irradiation data.

# Solar-to-Hydrogen Efficiency

Parameter | Value | Comment
--- | --- | ---
STH (%) | 0.3 | 30% STH Limit value from PEC Type 4 model (maximum possible STH efficiency ca. 40% for multi junction device based on Hellgardt 2018).

# Land Area Requirement

Parameter | Value | Comment
--- | --- | ---
Cell Angle (degree) | 35 | Used for total land area calculation.
South Spacing (m) | 6.71 | n/a
East/West Spacing (m) | 17.3 | n/a

# Direct Capital Costs - Water Management

Parameter | Value | Path | Comment
--- | --- | --- | ---
Water pump ($) | 213.0 | None | Based on Pinaud 2013.
Water Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value | n/a
Water Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value | n/a
Water Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value | n/a
Water Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value | n/a

# Direct Capital Costs - Gas Processing

Parameter | Value | Path | Comment
--- | --- | --- | ---
Condenser ($) | 7098.0 | None | Based on Pinaud 2013.
Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value | n/a
Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value | n/a
Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value | n/a
Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value | n/a

# Direct Capital Costs - Control System

Parameter | Path | Value | Comment
--- | --- | --- | ---
PLC ($) | None | 3000.0 | Based on Pinaud 2013.
Control Room Building ($) | None | 17527.0 | n/a
Control Room Wiring Panel ($) | None | 3000.0 | n/a
Computer and Monitor ($) | None | 1500.0 | n/a
Labview Software ($) | None | 4299.0 | n/a
Water Level Controllers (cost per cell, $) | PEC Cells > Number > Value | 50.0 | n/a
Pressure Sensors (cost per cell, $) | PEC Cells > Number > Value | 3.333 | n/a
Hydrogen Area Sensors (cost per cell, $) | PEC Cells > Number > Value | 73.42 | n/a
Hydrogen Flow Meter ($) | None | 5500.0 | n/a
Instrument Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.252 | n/a
Power Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.1256 | n/a
Conduit (cost per cell, $) | PEC Cells > Number > Value | 3.759 | n/a

# Direct Capital Costs - Installation Costs

Parameter | Path | Value | Comment
--- | --- | --- | ---
Piping Installation (per cell, $) | PEC Cells > Number > Value | 5.65 | Based on Pinaud 2013.
Reactor Installation (per m2 of solar collection area) | Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value | 22.0 | n/a
Pump Installation (% of pump cost) | Direct Capital Costs - Water Management > Water pump ($) > Value | 0.3 | n/a
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 0.3 | n/a
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 0.3 | n/a

# Indirect Capital Costs

Parameter | Path | Value | Comment
--- | --- | --- | ---
Engineering and Design (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.07 | Based on Pinaud 2013.
Process Contingency (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.2 | n/a
Up-Front Permitting Costs (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.005 | n/a
Site Preparation (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.01 | n/a

# Non-Depreciable Capital Costs

Parameter | Value | Comment
--- | --- | ---
Cost of land ($ per acre) | 500.0 | Land cost based on Pinaud 2013.

# Fixed Operating Costs

Parameter | Full Name | Value | Comment
--- | --- | --- | ---
area | Area per staff (m2) | 60000 | Based on Pinaud et al. 2013, smaller area per staff compared to PV+E and photocatalytic model due to smaller size of individual units, more connections and sensors.
supervisor | Shift supervisor | 1 | n/a
shifts | Shifts | 3 | n/a
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0 | n/a

# Other Fixed Operating Costs

Parameter | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 0.2 | Based on Pinaud 2013.
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 0.02 | n/a
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.005 | n/a
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0 | n/a

# Unplanned Replacement

Parameter | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.005 | Based on Pinaud 2013.

# Methods - SensitivityAnalysis

Parameter | Method Name | Arguments
--- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | {'show': False, 'save': False, 'fig_width': 8, 'label_offset': 0.12, 'lim_extra': 0.25, 'right': 0.97}

# CostContributionsAnalysis - Deactivate

Parameter
---

# Methods - CostContributionsAnalysis

Parameter | Method Name | Arguments
--- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot', 'show': False, 'save': False}
cost_breakdown_plot_capital | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot_Capital', 'show': False, 'save': False, 'plugin': 'Finance.CapitalCostPlugin', 'plugin_property': 'direct_contributions'}


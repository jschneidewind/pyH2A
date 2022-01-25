# Workflow

Name | Type | Description | Position
--- | --- | --- | ---
Hourly_Irradiation_Plugin | plugin | Plugin to calculate solar irradiation from typical meteorological year data | 0
PEC_Plugin | plugin | Plugin to model photoelectrochemical water splitting | 2
Multiple_Modules_Plugin | plugin | Modelling of module plant modules, adjustment of labor requirement | 3

# Display Parameters

Name | Value
--- | ---
Name | PEC Type 3
Color | darkred

# Technical Operating Parameters and Specifications

Name | Value | Path | Full Name
--- | --- | --- | ---
Operating Capacity Factor (%) | 90.0%
Plant Design Capacity (kg of H2/day) | 1,000
Plant Modules | 10 | None | 10 identical modules, only affects labor requirement calculation.

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# Hourly Irradiation

Name | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Location: Dagget, CA, USA

# Irradiance Area Parameters

Name | Value | Comment
--- | --- | ---
Module Tilt (degrees) | 0 | Two axis tracking, module tilt and array azimuth change are not relevant.
Array Azimuth (degrees) | 0
Nominal Operating Temperature (Celsius) | 45 | Temperature is stabilized by intrinsic water cooling.
Mismatch Derating | 98%
Dirt Derating | 98% | Values taken from Chang 2020, analogues to silicon PV
Temperature Coefficient (per Celsius) | 0.0% | No assumed efficiency loss with higher temperature.

# Solar Input

Name | Value | Path | Comment
--- | --- | --- | ---
Mean solar input (kWh/m2/day) | Hourly Irradiation > Mean solar input two axis tracking (kWh/m2/day) > Value | None | Two axis tracking irradiation from hourly irradiation data.

# Solar-to-Hydrogen Efficiency

Name | Value | Comment
--- | --- | ---
STH (%) | 30.0% | 30% STH Limit value from PEC Type 4 model (maximum possible STH efficiency ca. 40% for multi junction device based on Hellgardt 2018).

# PEC Cells

Name | Value | Comment
--- | --- | ---
Cell Cost ($/m2)| 700.0 | Price of III-V solar cells as reference, approximate $/W to $/m2 conversion formula: Cost ($/W) * conversion_efficiency (%) * 1000 W/m2 = Cost ($/m2), Reference: Horowitz 2018 (NREL), 70 $/W, assuming 30% efficiency = 21,000 $/m2. 30-fold cost reduction analogous to 30-fold cost reduction for photocatalyst in photocatalytic model.
Lifetime (years) | 3.0 | 9-fold lifetime increase relative to base case (0.33 years).
Length (m) | 6 | Based on sizing in Pinaud 2013.
Width (m) | 0.3 | Based on sizing in Pinaud 2013.

# Land Area Requirement

Name | Value | Comment
--- | --- | ---
Cell Angle (degree) | 35 | Used for total land area calculation.
South Spacing (m) | 6.71
East/West Spacing (m) | 17.3

# Direct Capital Costs - Water Management

Name | Value | Path | Comment
--- | --- | --- | ---
Water pump ($) | 213.0 | None | Based on Pinaud 2013.
Water Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value
Water Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value
Water Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value
Water Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value

# Direct Capital Costs - Gas Processing

Name | Value | Path | Comment
--- | --- | --- | ---
Condenser ($) | 7,098.0 | None | Based on Pinaud 2013.
Manifold Piping ($ per cell) | 11.58 | PEC Cells > Number > Value
Collection Piping ($ per cell) | 1.502 | PEC Cells > Number > Value
Column Collection Piping ($ per cell) | 1.1015 | PEC Cells > Number > Value
Final Collection Piping ($ per cell) | 0.231 | PEC Cells > Number > Value

# Direct Capital Costs - Control System

Name | Path | Value | Comment
--- | --- | --- | ---
PLC ($) | None | 3,000.0 | Based on Pinaud 2013.
Control Room Building ($) | None | 17,527.0
Control Room Wiring Panel ($) | None | 3,000.0
Computer and Monitor ($) | None | 1,500.0
Labview Software ($) | None | 4,299.0
Water Level Controllers (cost per cell, $) | PEC Cells > Number > Value | 50.0
Pressure Sensors (cost per cell, $) | PEC Cells > Number > Value | 3.333
Hydrogen Area Sensors (cost per cell, $) | PEC Cells > Number > Value | 73.42
Hydrogen Flow Meter ($) | None | 5,500.0
Instrument Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.252
Power Wiring (cost per cell, $) | PEC Cells > Number > Value | 0.1256
Conduit (cost per cell, $) | PEC Cells > Number > Value | 3.759

# Direct Capital Costs - Installation Costs

Name | Path | Value | Comment
--- | --- | --- | ---
Piping Installation (per cell, $) | PEC Cells > Number > Value | 5.65 | Based on Pinaud 2013.
Reactor Installation (per m2 of solar collection area) | Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value | 22.0
Pump Installation (% of pump cost) | Direct Capital Costs - Water Management > Water pump ($) > Value | 30%
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 30%
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 30%

# Indirect Capital Costs

Name | Path | Value | Comment
--- | --- | --- | ---
Engineering and Design (% of total direct capital costs)| Direct Capital Costs > Total > Value  | 7% | Based on Pinaud 2013.
Process Contingency (% of total direct capital costs) | Direct Capital Costs > Total > Value | 20.0%
Up-Front Permitting Costs (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
Site Preparation (% of total direct capital costs) | Direct Capital Costs > Total > Value | 1%

# Non-Depreciable Capital Costs

Name | Value | Comment
--- | --- | ---
Cost of land ($ per acre) | 500.0 | Land cost based on Pinaud 2013.

# Fixed Operating Costs

Name | Full Name | Value | Comment
--- | --- | --- | ---
area | Area per staff (m2) | 60,000 | Based on Pinaud et al. 2013, smaller area per staff compared to PV+E and photocatalytic model due to smaller size of individual units, more connections and sensors.
supervisor | Shift supervisor | 1
shifts | Shifts | 3
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 20.0% | Based on Pinaud 2013.
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 2.0%
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.5%
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Comment
--- | --- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 0.16 | kWh/kg H2 | pyH2A.Lookup_Tables.Utility_Cost~Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh | Electricity usage based on Pinaud 2013.
Process Water | 2.369 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to ca. 0.0023 $/gal), based on Kibria 2021 and Driess 2021.

# Unplanned Replacement

Name | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.5% | Based on Pinaud 2013.

# Sensitivity_Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH efficiency | value | 15%; 40%
PEC Cells > Cell Cost ($/m2) > Value | PEC cell cost (\$/m^{2}) | value | 350; 1,400
PEC Cells > Lifetime (years) > Value | PEC cell lifetime (years) | value | 1.5; 6

# Methods - Sensitivity_Analysis

Name | Method Name | Arguments
--- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | {'show': False, 'save': False, 'fig_width': 8, 'label_offset': 0.12, 'lim_extra': 0.25, 'right': 0.97}

# Cost_Contributions_Analysis - Deactivate

# Methods - Cost_Contributions_Analysis

Name | Method Name | Arguments
--- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot', 'show': False, 'save': False}
cost_breakdown_plot_capital | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot_Capital', 'show': False, 'save': False, 'plugin': 'Capital_Cost_Plugin', 'plugin_property': 'direct_contributions'}
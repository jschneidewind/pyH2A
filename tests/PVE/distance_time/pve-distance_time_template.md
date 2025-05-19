# Workflow

Parameter | Type | Position
--- | --- | ---
[...] | plugin, optional | int, optional
Energy.HourlyIrradiationPlugin | plugin | 0
Energy.PhotovoltaicPlugin | plugin | 0
Hydrogen.ElectrolyzerPlugin | plugin | 0
Energy.BatteryPlugin | plugin | 0
Hydrogen.StoredPowerElectrolysisPlugin | plugin | 0
Hydrogen.ReverseOsmosisPlugin | plugin | 2
Energy.PowerManagementPlugin | plugin | 2
Background.MultipleModulesPlugin | plugin | 3

# Construction

Parameter | Value | Full Name
--- | --- | ---
[...] | float | n/a
capital perc 1st | 1.0 | % of capital spent in 1st year of construction

# Technical Operating Parameters and Specifications

Parameter | Value | Comment
--- | --- | ---
Maximum Output at Gate | float, optional | n/a
New Plant Design Capacity (kg of H2/day) | float, optional | n/a
Scaling Ratio | float, optional | n/a
Capital Scaling Exponent | float, optional | n/a
Labor Scaling Exponent | float, optional | n/a
Plant Modules | 10 | Modelling of 10 modules for calculation of staff cost to facilitate comparison with PEC and photocatalytic model.

# Power Consumption

Parameter | Value | Type
--- | --- | ---
[...] | nd.array, optional | str, optional

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

Parameter | Frequency (years) | Cost ($) | Path | Comment
--- | --- | --- | --- | ---
[...] | float | float | n/a | n/a
Electrolyzer Stack Replacement | n/a | 0.4 | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Chang 2020

# [...] Unplanned Replacement [...]

Parameter | Value
--- | ---
[...] | float

# [...] Other Fixed Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Utilities

Parameter | Cost | Usage per kg H2 | Price Conversion Factor | Path | Usage Path | Usage Unit | Cost Unit | Comment
--- | --- | --- | --- | --- | --- | --- | --- | ---
[...] | float, ndarray or str | float | float | str, optional | str, optional | n/a | n/a | n/a
Process Water | 0.0006 | 10 | 1.0 | n/a | n/a | L/kg H2 | $/L | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to 0.0006 $/L), based on Kibria 2021 and Driess 2021.

# [...] Other Variable Operating Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Monte_Carlo_Analysis

Parameter | Value | Comment
--- | --- | ---
Output File | str, optional | n/a
Samples | 50000 | Number of samples in Monte Carlo simulation.
Target Price Range ($) | 1.5; 1.6 | n/a
Input File | tests/PVE/distance_time/pve-monte_carlo-results.csv | n/a

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | ---
[...] | str | str | str | int, optional | n/a
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 220 | 0 | Based on Waldau 2021 PV CAPEX projection for 2050 (PV module learning rate of 25%, BOS learning rate of 7.5%, base PV growth scenario).
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1 | CAPEX reduction to 200 $/kW in 2050 based on IRENA Green Hydrogen 2020, learning curve model Waldau 2021 (using their cost reduction factor of ca. 4-5 until 2050 due to learning).
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.025 | 2 | Maximum efficiency: 0.02538 kg H2/kWh, Chang 2020 (based on reaction enthalpy).
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack repl. (fr. E-CAPEX) | value | Base; 20% | 3 | Decreasing stack replacement cost to 20% of electrolyzer CAPEX.

# Development_Distance_Time_Analysis

Parameter | Year | Value
--- | --- | ---
Extrapolation Limit | int | n/a
Input File | n/a | tests/PVE/distance_time/pve-historical_data.csv
Log Normalization | n/a | True
Base Year | n/a | 2020
Extrapolation Limit Year | n/a | 2060

# Display Parameters

Parameter | Value
--- | ---
Name | PV + E
Color | darkblue

# Hourly Irradiation

Parameter | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Location: Dagget, CA, USA

# Irradiance Area Parameters

Parameter | Value | Comment
--- | --- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value | Module tilt equal to latitude of location.
Array Azimuth (degrees) | 180 | n/a
Nominal Operating Temperature (Celsius) | 45 | n/a
Mismatch Derating | 0.98 | Based on Chang 2020.
Dirt Derating | 0.98 | Based on Chang 2020.
Temperature Coefficient (per Celsius) | -0.004 | Based on Chang 2020.

# Irradiation Used

Parameter | Value | Comment
--- | --- | ---
Data | Hourly Irradiation > Horizontal Single Axis Tracking (kW) > Value | Single axis tracking based on Chang 2020.

# CAPEX Multiplier

Parameter | Value | Full Name
--- | --- | ---
Multiplier | 1.0 | CAPEX multiplier for every 10-fold increase of system size.

# Electrolyzer

Parameter | Value
--- | ---
Nominal Power (kW) | 5500.0
CAPEX Reference Power (kW) | 1000.0
Power requirement increase per year | 0.01
Minimum capacity | 0.1
Conversion efficiency (kg H2/kWh) | 0.02
Replacement time (h) | 40000.0

# Electrolysis Using Stored Power

Parameter | Value | Comment
--- | --- | ---
Fraction of stored power used for electrolysis | 0.95 | Additional electrolysis using stored power

# Photovoltaic

Parameter | Value | Path
--- | --- | ---
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value
CAPEX Reference Power (kW) | 1000.0 | n/a
Power loss per year | 0.005 | n/a
Efficiency | 0.22 | n/a

# Reverse Osmosis

Parameter | Value | Comment
--- | --- | ---
Power Demand (kWh/m3) | 2.71 | based on Hausmann 2021 and Kim 2008 (this was chosen for a purity of < 10 ppm of disolved salts in the obtained water), kWh per m3 of sea water
Average daily operating hours | 4 | Assumption that reverse osmosis runs for 4 h/day, relevant for scaling of reverse osmosis plant
Recovery Rate | 0.4 | Fraction of fresh water obtained from given volume of sea water, based Palmer 2021 and Tewlour 2022

# Battery

Parameter | Value | Comment
--- | --- | ---
Design Capacity (kWh) | 800000 | Full design capacity
Lowest discharge level | 0.2 | Lowest level to which battery can be discharged
Capacity loss per year | 0.01 | Loss of capacity per year
Round trip efficiency | 1.0 | For lithium ion battery
Weight per capacity (kg/kWh) | 6.94 | n/a

# Grid Electricity

Parameter | Value
--- | ---
Cost ($/kWh) | 10000.12

# Direct Capital Costs - PV

Parameter | Value | Path | Comment
--- | --- | --- | ---
PV CAPEX ($/kW) | 818.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value | Based on Chang 2020, Chiesa 2021 Middle East PV installation cost, Shah 2021.

# Direct Capital Costs - Electrolyzer

Parameter | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer CAPEX ($/kW) | 784.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value | Based on Chang 2020, IRENA 2020 Green Hydrogen (PEM System CAPEX 700 - 1400 $/kg), Shah 2021.

# Non-Depreciable Capital Costs

Parameter | Value | Comment
--- | --- | ---
Cost of land ($ per acre) | 500.0 | Same as PEC and Photocatalytic model, based on Pinaud 2013.

# Fixed Operating Costs

Parameter | Full Name | Value | Comment
--- | --- | --- | ---
area | Area per staff (m2) | 405000 | Same as photocatalytic model, solar collection area that can be overseen by one staff member.
supervisor | Shift supervisor | 1 | Same as PEC and photocatalytic model, number of shift supervisors.
shifts | Shifts | 3 | Same as PEC and photocatalytic model, number of shifts per day.
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0 | Same as PEC and photocatalytic model.

# Other Fixed Operating Costs

Parameter | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer OPEX (% of CAPEX) | 0.02 | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Stolten 2020, Shah 2021.
PV OPEX (% of CAPEX) | 0.02 | Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | Based on Stolten 2020.

# Methods - Development_Distance_Time_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
plot_distance_histogram_log | plot_distance_histogram | {'show': False, 'save': False, 'dpi': 400, 'pdf': True, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
plot_distance_cost_log | plot_distance_cost_relationship | {'show': False, 'save': False, 'dpi': 300, 'pdf': False, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
plot_distance_time | plot_distance_time_relationship | Arguments - Time Analysis - distance_time_plot
plot_distance_time_no_table | plot_distance_time_relationship | Arguments - Time Analysis - distance_time_plot_no_table

# Arguments - Time Analysis - distance_time_plot

Parameter | Value
--- | ---
show | True
save | False
dpi | 500
pdf | True
color_future | False
image_kwargs | {'path': 'pyH2A.Other~PV_E_Clipart.png'}

# Arguments - Time Analysis - distance_time_plot_no_table

Parameter | Value
--- | ---
show | False
save | False
name | Distance_Time_Relationship_No_Table
dpi | 500
pdf | False
parameter_table | False
color_future | False
target_distances | [0.5, 0.6]
plot_kwargs | {'left': 0.34, 'right': 0.96, 'bottom': 0.13, 'top': 0.96, 'fig_width': 6.2, 'fig_height': 4.0}
image_kwargs | {'x': -0.37, 'zoom': 0.092, 'y': 0.5, 'path': 'pyH2A.Other~PV_E_Clipart.png'}

# Methods - Monte_Carlo_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
target_parameters | plot_target_parameters_by_distance | {'show': False}


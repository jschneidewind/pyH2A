# Workflow

Name | Type | Position
--- | --- | ---
Energy.HourlyIrradiationPlugin | plugin | 0
Energy.PhotovoltaicPlugin | plugin | 0
Hydrogen.ElectrolyzerPlugin | plugin | 0
Energy.BatteryPlugin | plugin | 0
Hydrogen.StoredPowerElectrolysisPlugin | plugin | 0
Hydrogen.ReverseOsmosisPlugin | plugin | 2
Energy.PowerManagementPlugin | plugin | 2
Background.MultipleModulesPlugin | plugin | 3

# Display Parameters

Name | Value
--- | ---
Name | PV + E
Color | darkblue

# Hourly Irradiation

Name | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Location: Dagget, CA, USA

# Irradiance Area Parameters

Name | Value | Comment
--- | --- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value | Module tilt equal to latitude of location.
Array Azimuth (degrees) | 180
Nominal Operating Temperature (Celsius) | 45
Mismatch Derating | 0.98 | Based on Chang 2020.
Dirt Derating | 0.98 | Based on Chang 2020.
Temperature Coefficient (per Celsius) | -0.4% | Based on Chang 2020.

# Irradiation Used

Name | Value | Comment
--- | --- | --- 
Data | Hourly Irradiation > Horizontal Single Axis Tracking (kW) > Value | Single axis tracking based on Chang 2020.

# Technical Operating Parameters and Specifications

Name | Value | Comment
--- | --- | ---
Plant Modules | 10 | Modelling of 10 modules for calculation of staff cost to facilitate comparison with PEC and photocatalytic model.

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of capital spent in 1st year of construction | 100%

# CAPEX Multiplier

Name | Value | Full Name
--- | --- | ---
Multiplier | 1.0 | CAPEX multiplier for every 10-fold increase of system size.

# Electrolyzer

Name | Value
--- | ---
Nominal Power (kW) | 5,500.0
CAPEX Reference Power (kW) | 1,000.0
Power requirement increase per year | 1.0%
Minimum capacity | 10.0%
Conversion efficiency (kg H2/kWh) | 0.02
Replacement time (h) | 40,000.0

# Electrolysis Using Stored Power

Name | Value | Comment
--- | --- | ---
Fraction of stored power used for electrolysis | 95% | Additional electrolysis using stored power

# Photovoltaic

Name | Value | Path
--- | --- | ---
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value
CAPEX Reference Power (kW) | 1,000.0
Power loss per year | 0.5%
Efficiency | 22%

# Reverse Osmosis

Name | Value | Comment
--- | --- | --- | ---
Power Demand (kWh/m3) | 2.71 | based on Hausmann 2021 and Kim 2008 (this was chosen for a purity of < 10 ppm of disolved salts in the obtained water), kWh per m3 of sea water
Average daily operating hours | 4 | Assumption that reverse osmosis runs for 4 h/day, relevant for scaling of reverse osmosis plant
Recovery Rate | 40.0% | Fraction of fresh water obtained from given volume of sea water, based Palmer 2021 and Tewlour 2022

# Battery

Name | Value | Comment
--- | --- | ---
Design Capacity (kWh) | 800000 | Full design capacity
Lowest discharge level | 20% | Lowest level to which battery can be discharged
Capacity loss per year | 1% | Loss of capacity per year
Round trip efficiency | 100% | For lithium ion battery
Weight per capacity (kg/kWh) | 6.94

# Grid Electricity

Name | Value
--- | ---
Cost ($/kWh) | 10000.12

# Direct Capital Costs - PV

Name | Value | Path | Comment
--- | --- | --- | ---
PV CAPEX ($/kW) | 818.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value | Based on Chang 2020, Chiesa 2021 Middle East PV installation cost, Shah 2021.

# Direct Capital Costs - Electrolyzer

Name | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer CAPEX ($/kW) | 784.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value | Based on Chang 2020, IRENA 2020 Green Hydrogen (PEM System CAPEX 700 - 1400 $/kg), Shah 2021.

# Non-Depreciable Capital Costs

Name | Value | Comment
--- | --- | ---
Cost of land ($ per acre) | 500.0 | Same as PEC and Photocatalytic model, based on Pinaud 2013.

# Fixed Operating Costs

Name | Full Name | Value | Comment
--- | --- | --- | ---
area | Area per staff (m2) | 405,000 | Same as photocatalytic model, solar collection area that can be overseen by one staff member.
supervisor | Shift supervisor | 1 | Same as PEC and photocatalytic model, number of shift supervisors.
shifts | Shifts | 3 | Same as PEC and photocatalytic model, number of shifts per day.
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0 | Same as PEC and photocatalytic model.

# Other Fixed Operating Costs

Name | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer OPEX (% of CAPEX) | 2% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Stolten 2020, Shah 2021.
PV OPEX (% of CAPEX) | 2% | Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | Based on Stolten 2020.

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Comment
--- | --- | --- | --- | --- | --- | ---
Process Water | 10 | L/kg H2 | 0.0006 | $/L | 1. | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to 0.0006 $/L), based on Kibria 2021 and Driess 2021.

# Planned Replacement

Name | Cost ($) | Path | Comment
--- | --- | --- | ---
Electrolyzer Stack Replacement | 40% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Chang 2020

# MonteCarloAnalysis

Name | Value | Comment
--- | --- | ---
Samples | 50,000 | Number of samples in Monte Carlo simulation.
Target Price Range ($) | 1.5; 1.6
Input File | tests/PVE/distance_time/pve-monte_carlo-results.csv

# Parameters - MonteCarloAnalysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | --- 
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 220 | 0 | Based on Waldau 2021 PV CAPEX projection for 2050 (PV module learning rate of 25%, BOS learning rate of 7.5%, base PV growth scenario).
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1 | CAPEX reduction to 200 $/kW in 2050 based on IRENA Green Hydrogen 2020, learning curve model Waldau 2021 (using their cost reduction factor of ca. 4-5 until 2050 due to learning).
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.025 | 2 | Maximum efficiency: 0.02538 kg H2/kWh, Chang 2020 (based on reaction enthalpy).
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack repl. (fr. E-CAPEX) | value | Base; 20% | 3 | Decreasing stack replacement cost to 20% of electrolyzer CAPEX.

# DevelopmentDistanceTimeAnalysis

Name | Value
--- | ---
Input File | tests/PVE/distance_time/pve-historical_data.csv
Log Normalization | True
Base Year | 2020
Extrapolation Limit Year | 2060

# Methods - DevelopmentDistanceTimeAnalysis

Name | Method Name | Arguments
--- | --- | ---
plot_distance_histogram_log | plot_distance_histogram | {'show': False, 'save': False, 'dpi': 400, 'pdf': True, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
plot_distance_cost_log | plot_distance_cost_relationship | {'show': False, 'save': False, 'dpi': 300, 'pdf': False, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
plot_distance_time | plot_distance_time_relationship | Arguments - Time Analysis - distance_time_plot
plot_distance_time_no_table | plot_distance_time_relationship | Arguments - Time Analysis - distance_time_plot_no_table

# Arguments - Time Analysis - distance_time_plot

Name | Value
--- | ---
show | True
save | False
dpi | 500
pdf | True
color_future | False
image_kwargs | {'path': 'pyH2A.Other~PV_E_Clipart.png'}

# Arguments - Time Analysis - distance_time_plot_no_table

Name | Value
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

# Methods - MonteCarloAnalysis

Name | Method Name | Arguments
--- | --- | ---
target_parameters | plot_target_parameters_by_distance | {'show': False}
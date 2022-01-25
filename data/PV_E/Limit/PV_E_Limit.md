# Workflow

Name | Type | Position
--- | --- | ---
Hourly_Irradiation_Plugin | plugin | 0
Photovoltaic_Plugin | plugin | 0
Multiple_Modules_Plugin | plugin | 3

# Display Parameters

Name | Value
--- | ---
Name | PV + E
Color | darkblue

# Hourly Irradiation

Name | Value
--- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv

# Irradiance Area Parameters

Name | Value | Comment
--- | --- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value
Array Azimuth (degrees) | 180
Nominal Operating Temperature (Celsius) | 45
Mismatch Derating | 0.98 | Based on Chang 2020
Dirt Derating | 0.98 | Based on Chang 2020
Temperature Coefficient (per Celsius) | -0.4% | Based on Chang 2020

# Irradiation Used

Name | Value | Comment
--- | --- | --- 
Data | Hourly Irradiation > Horizontal Single Axis Tracking (kW) > Value | Single axis tracking based on Chang 2020

# Technical Operating Parameters and Specifications

Name | Value | Comment
--- | --- | ---
Plant Modules | 10 | Modelling of 10 modules for calculation of staff cost to facilitate comparison with PEC and photocatalytic model

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# CAPEX Multiplier

Name | Value | Full Name
--- | --- | ---
Multiplier | 1.0 | CAPEX multiplier for every 10-fold increase of system size

# Electrolyzer

Name | Value | Comment
--- | --- | ---
Nominal Power (kW) | 5,500.0 | Production of ca. 1 t of H2 per day to compare with PEC and photocatalytic models
CAPEX Reference Power (kW) | 1,000.0
Power requirement increase per year | 0.3% | Based on Chang 2020
Minimum capacity | 10.0% | Based on Chang 2020
Conversion efficiency (kg H2/kWh) | 0.025 | Based on Chang 2020
Replacement time (h) | 80,000.0 | Based on Chang 2020

# Photovoltaic

Name | Value | Path | Comment
--- | --- | --- | --- 
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value | Optimal PV oversize ratio, same as Chang 2020
CAPEX Reference Power (kW) | 1,000.0
Power loss per year | 0.5% | Based on Chang 2020
Efficiency | 22% | None | Only for area calculation

# Direct Capital Costs - PV

Name | Value | Path | Comment
--- | --- | --- | ---
PV CAPEX ($/kW) | 220.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value | Based on Chang 2020, Chiesa 2021 Middle East PV installation cost, Shah 2021

# Direct Capital Costs - Electrolyzer

Name | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer CAPEX ($/kW) | 200.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value | Based on Chang 2020, IRENA 2020 Green Hydrogen (PEM System CAPEX 700 - 1400 $/kg), Shah 2021

# Non-Depreciable Capital Costs

Name | Value | Path | Comment
--- | --- | --- | ---
Cost of land ($ per acre) | 500.0 | None | Same as PEC and Photocatalytic model, based on Pinaud 2013

# Fixed Operating Costs

Name | Full Name | Value | Comment
--- | --- | --- | ---
area | Area per staff (m2) | 405,000 | Same as photocatalytic model
supervisor | Shift supervisor | 1 | Same as PEC and photocatalytic model
shifts | Shifts | 3 | Same as PEC and photocatalytic model
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0 | Same as PEC and photocatalytic model

# Other Fixed Operating Costs

Name | Value | Path | Comment
--- | --- | --- | ---
Electrolyzer OPEX (% of CAPEX) | 2% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Stolten 2020, Shah 2021
PV OPEX (% of CAPEX) | 2% | Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | Based on Stolten 2020

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Path | Usage Path | Comment
--- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Process Water | 10 | L/kg H2 | 0.0006 | $/L | 1. | None | None | None | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to 0.0006 $/L), based on Kibria 2021 and Driess 2021

# Planned Replacement

Name | Cost ($) | Path | Comment
--- | --- | --- | ---
Electrolyzer Stack Replacement | 20% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Based on Chang 2020

# Cost_Contributions_Analysis - Deactivate

# Methods - Cost_Contributions_Analysis 

Name | Method Name | Arguments
--- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot', 'show': False, 'save': False}
cost_breakdown_plot_capital | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot_Capital', 'show': False, 'save': False, 'plugin': 'Capital_Cost_Plugin', 'plugin_property': 'direct_contributions', 'fig_height': 3, 'bottom': 0.2}

# Sensitivity_Analysis - Deactivate

Parameter | Name | Type | Values
--- | --- | --- | ---
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack repl. cost (% of E-CAPEX) | value | 10%; 40%
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | PV CAPEX (\$/kW) | value | 100; 400
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Electrolyzer CAPEX (\$/kW) | value | 100; 400
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | Electrolyzer efficiency (kg H_{2}/kWh) | value | 0.02; 0.0253
Photovoltaic > Power loss per year > Value | PV power loss per year | value | 0.25%; 1.0%
Electrolyzer > Power requirement increase per year > Value | Electrolyzer power increase per year | value | 0.15%; 0.6%

# Methods - Sensitivity_Analysis

Name | Method Name | Arguments
--- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | {'show': False, 'save': False, 'fig_width': 8, 'label_offset': 0.12, 'lim_extra': 0.25, 'fig_height': 5.4, 'bottom': 0.1, 'top': 0.98}

# Monte_Carlo_Analysis - Deactivate

Name | Value
--- | ---
Samples | 1000
Target Price Range ($) | 1.5; 2.5
Input File | pyH2A.Example~PV_E_Monte_Carlo.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | --- 
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 220 | 0 | Based on Waldau 2021 PV CAPEX projection for 2050 (PV module learning rate of 25%, BOS learning rate of 7.5%, base PV growth scenario)
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1 | CAPEX reduction to 200 $/kW in 2050 based on IRENA Green Hydrogen 2020, learning curve model Waldau 2021 (using their cost reduction factor of ca. 4-5 until 2050 due to learning).
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.025 | 2 | Maximum efficiency: 0.02538 kg H2/kWh, Chang 2020 (based on reaction enthalpy)
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack Replacement (fr. E-CAPEX) | value | Base; 20% | 3 | Decreasing stack replacement cost to 20% of electrolyzer CAPEX.

# Methods - Monte_Carlo_Analysis

Name | Method Name | Arguments
--- | --- | ---
distance_histogram | plot_distance_histogram | {'show': False}
distance_cost_relationship | plot_distance_cost_relationship | {'show': True}
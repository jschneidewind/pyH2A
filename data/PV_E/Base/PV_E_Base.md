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

Name | Value | Comment
--- | --- | ---
Nominal Power (kW) | 5,500.0 | Production of ca. 1 t of H2 per day to compare with PEC and photocatalytic models.
CAPEX Reference Power (kW) | 1,000.0
Power requirement increase per year | 0.3% | Based on Chang 2020
Minimum capacity | 10.0% | Based on Chang 2020, minimum capacity for electrolyzer to operate.
Conversion efficiency (kg H2/kWh) | 0.0185 | Based on Chang 2020
Replacement time (h) | 80,000.0 | Based on Chang 2020, operating time after which electrolyzer stacks have to be replaced.

# Photovoltaic

Name | Value | Path | Comment
--- | --- | --- | --- 
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value | Optimal PV oversize ratio, same as Chang 2020
CAPEX Reference Power (kW) | 1,000.0
Power loss per year | 0.5% | Based on Chang 2020
Efficiency | 22% | None | Only used for area calculation.

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

# Sensitivity_Analysis - Deactivate

Parameter | Name | Type | Values
--- | --- | --- | ---
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack repl. cost (% of E-CAPEX) | value | 20%; 80%
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | PV CAPEX (\$/kW) | value | 400; 1600
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Electrolyzer CAPEX (\$/kW) | value | 400; 1600
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | Electrolyzer efficiency (kg H_{2}/kWh) | value | 0.015; 0.025
Photovoltaic > Power loss per year > Value | PV power loss per year | value | 0.25%; 1.0%
Electrolyzer > Power requirement increase per year > Value | Electrolyzer power increase per year | value | 0.15%; 0.6%

# Waterfall_Analysis - Deactivate

Parameter | Name | Type | Value | Show Percent
--- | --- | --- | --- | ---
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$)/ kWh(Electricity) | value | 0.025
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$/kW(PV) | value | 220
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$/kW(Electro- lyzer) | value | 200
Planned Replacement > Electrolyzer Stack Replacement > Cost ($)| Stack replacement (%E-CAPEX) | value | 20% | True

# Monte_Carlo_Analysis

Name | Value | Comment
--- | --- | ---
Samples | 50,000 | Number of samples in Monte Carlo simulation.
Target Price Range ($) | 1.5; 1.6
Input File | ./PV_E/Base/Monte_Carlo_Output.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | --- 
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 220 | 0 | Based on Waldau 2021 PV CAPEX projection for 2050 (PV module learning rate of 25%, BOS learning rate of 7.5%, base PV growth scenario).
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1 | CAPEX reduction to 200 $/kW in 2050 based on IRENA Green Hydrogen 2020, learning curve model Waldau 2021 (using their cost reduction factor of ca. 4-5 until 2050 due to learning).
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.025 | 2 | Maximum efficiency: 0.02538 kg H2/kWh, Chang 2020 (based on reaction enthalpy).
Planned Replacement > Electrolyzer Stack Replacement > Cost ($) | Stack repl. (fr. E-CAPEX) | value | Base; 20% | 3 | Decreasing stack replacement cost to 20% of electrolyzer CAPEX.

# Cost_Contributions_Analysis - Deactivate

# Methods - Cost_Contributions_Analysis 

Name | Method Name | Arguments
--- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot', 'show': False, 'save': False}
cost_breakdown_plot_capital | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot_Capital', 'show': False, 'save': False, 'plugin': 'Capital_Cost_Plugin', 'plugin_property': 'direct_contributions', 'fig_height': 3, 'bottom': 0.2}

# Methods - Sensitivity_Analysis

Name | Method Name | Arguments
--- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | {'show': False, 'save': False, 'fig_width': 8, 'label_offset': 0.12, 'lim_extra': 0.25, 'fig_height': 5.4, 'bottom': 0.1, 'top': 0.98, 'format_cutoff': 7}

# Methods - Waterfall_Analysis

Name | Method Name | Arguments
--- | --- | ---
waterfall_chart | plot_waterfall_chart | {'show': True, 'save': False, 'fig_width': 9, 'width': 0.55}

# Methods - Monte_Carlo_Analysis

Name | Method Name | Arguments
--- | --- | ---
distance_cost_relationship | plot_distance_cost_relationship | Arguments - MC Analysis - distance_cost
distance_histogram | plot_distance_histogram | {'show': False, 'xlabel': True, 'save': False, 'pdf': True, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
colored_scatter | plot_colored_scatter | Arguments - MC Analysis - colored_scatter
target_parameters | plot_target_parameters_by_distance | {'show': False}

# Arguments - MC Analysis - colored_scatter

Name | Value
--- | ---
show | False
save | False
pdf | False
dpi | 500
base_string | Base
title_string | Target cost range: 
plot_kwargs | {'left': 0.32, 'right': 0.94, 'bottom': 0.13, 'top': 0.92, 'fig_width': 6.5, 'fig_height': 4.0}
image_kwargs | {'x': -0.41, 'zoom': 0.092, 'y': 0.5, 'path': 'pyH2A.Other~PV_E_Clipart.png'}

# Arguments - MC Analysis - distance_cost

Name | Value
--- | ---
legend_loc | upper right
log_scale | True
plot_kwargs | {'show': False, 'save': False, 'dpi': 300, 'left': 0.09, 'right': 0.5, 'bottom': 0.15, 'top': 0.95, 'fig_width': 9, 'fig_height': 3.5}
table_kwargs | {'ypos': 0.5, 'xpos': 1.05, 'height': 0.5}
image_kwargs | {'path': 'pyH2A.Other~PV_E_Clipart.png', 'x': 1.6, 'zoom': 0.095, 'y': 0.2}

# Comparative_MC_Analysis - Deactivate

Name | Value | Image
--- | --- | ---
pec | ./PEC/Base/PEC_Base.md | pyH2A.Other~PEC_Clipart.png
photocatalytic | ./Photocatalytic/Base/Photocatalytic_Base.md | pyH2A.Other~Photocatalytic_Clipart.png
pv_e | ./PV_E/Base/PV_E_Base.md | pyH2A.Other~PV_E_Clipart.png

# Methods - Comparative_MC_Analysis

Name | Method Name | Arguments
--- | --- | ---
comparative_distance_histogram | plot_comparative_distance_histogram | Arguments - Comparative MC Analysis - distance_histogram
comparative_distance_cost_relationship | plot_comparative_distance_cost_relationship | Arguments - Comparative MC Analysis - distance_cost
comparative_distance_combined | plot_combined_distance | {'show': False, 'save': False, 'left': 0.06, 'fig_width': 13, 'dist_kwargs': {'legend_loc': 'upper right', 'log_scale': True}, 'table_kwargs': {'colWidths': [0.65, 0.25, 0.12, 0.25]}, 'hist_kwargs': {'title_string': 'Target cost range:'}}

# Arguments - Comparative MC Analysis - distance_cost

Name | Value
--- | ---
show | False
save | False
pdf | False
dpi | 300 
fig_height | 5
fig_width | 9
top | 0.98
bottom | 0.1
dist_kwargs | {'log_scale': True, 'ylabel_string': 'Levelized cost of $H_{2}$ / \$/kg($H_{2}$)'}
table_kwargs | {'format_cutoff': 7, 'height': 0.3, 'colWidths': [0.65, 0.2, 0.09, 0.2]}

# Arguments - Comparative MC Analysis - distance_histogram

Name | Value
--- | ---
show | False
save | False
pdf | False
dpi | 500
fig_width | 5.5
fig_height | 4.5
left | 0.35
right | 0.97
bottom | 0.12
top | 0.93
hist_kwargs | {'show_parameter_table': False}
image_kwargs | {'x': -0.38}


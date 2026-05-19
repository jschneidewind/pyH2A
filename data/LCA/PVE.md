# Life Cycle Assessment 

Name | Value
--- | ---
Matrix Folder | data/LCA/LCA_Test_PVE_EF

# LCA - PVE Components

Name | Value | Unit | UUID
--- | --- | --- | ---
Total H2 Production |Technical Operating Parameters and Specifications > Output per Year at Gate > Value | kg | 50e1c844-e481-4c14-a3ca-1948f1d2fe37
PV Area | Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value | m2 | 0c88e490-56a5-3099-807c-06645527c90e
Electrolyzer unit number | Electrolyzer > Number of electrolyzers required > Value | - | 98f950b2-39b0-4374-a400-05984b438be9
Battery weight | Battery > Mass (kg) > Value | kg | c341bfcb-5959-3a70-839e-913e8250b237
Reverse Osmosis Units | Reverse Osmosis > Number of devices required > Value | - | 056a11ab-0a7a-38dd-a1d3-4058c2a8662d

# Workflow

Name | Type | Position
--- | --- | ---
Hourly_Irradiation_Plugin | plugin | 0
Photovoltaic_Plugin | plugin | 0
Electrolyzer_Plugin | plugin | 0
Battery_Plugin | plugin | 0
Stored_Power_Electrolysis_Plugin | plugin | 0
Reverse_Osmosis_Plugin | plugin | 2
Power_Management_Plugin | plugin | 2
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
Unit Nominal Power (kW) | 3,900.0 | Size of one electrolyzer unit used to calculate required unit count based on Palmer et al. 2021 paper.

# Electrolysis Using Stored Power

Name | Value | Comment
--- | --- | ---
Fraction of stored power used for electrolysis | 0% | Additional electrolysis using stored power

# Photovoltaic

Name | Value | Path | Comment
--- | --- | --- | --- 
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value | Optimal PV oversize ratio, same as Chang 2020
CAPEX Reference Power (kW) | 1,000.0
Power loss per year | 0.5% | None | Based on Chang 2020
Efficiency | 20% | None | Only used for area calculation.

# Battery

Name | Value | Comment
--- | --- | ---
Design Capacity (kWh) | 800000 | Full design capacity
Lowest discharge level | 20% | Lowest level to which battery can be discharged
Capacity loss per year | 1% | Loss of capacity per year
Round trip efficiency | 100% | For lithium ion battery
Energy density (kWh/kg) | 0.2 | Battery specific energy for analyses and Monte Carlo sampling

# Reverse Osmosis

Name | Value | Comment
--- | --- | --- | ---
Power Demand (kWh/m3) | 2.71 | based on Hausmann 2021 and Kim 2008 (this was chosen for a purity of < 10 ppm of disolved salts in the obtained water), kWh per m3 of sea water
Average daily operating hours | 4 | Assumption that reverse osmosis runs for 4 h/day, relevant for scaling of reverse osmosis plant
Recovery Rate | 40.0% | Fraction of fresh water obtained from given volume of sea water, based Palmer 2021 and Tewlour 2022
Device throughput (L/year) | 6.23e10 | Throughput of one reverse osmosis device used to calculate number of required devices

# Power Consumption

Name | Value | Type
--- | --- | ---
Test Consumer | 0 | on_demand

# Direct Capital Costs - Reverse Osmosis

Name | Value | Path | Comment 
--- | --- | --- | ---
Reverse Osmosis CAPEX ($ per m3/h capacity) | 0 | Reverse Osmosis > Capacity (m3/h) > Value | Based on https://samcotech.com/much-reverse-osmosis-nanofiltration-membrane-systems-cost/, Conversion factor of 4.5 from GPM to m3/h (6000 $/m3/h)

# Direct Capital Costs - Battery

Name | Value | Path
--- | --- | ---
Battery CAPEX ($/kWh) | 0 | Battery > Design Capacity (kWh) > Value

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

# Grid Electricity

Name | Value
--- | ---
Cost ($/kWh) | 10000.12

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
Samples | 50000 | Number of samples in Monte Carlo simulation.
Dependent Variable | Climate change | Supported: h2_cost, Climate change, or Cumulative energy demand.
Target Response Range | 0; 100 | Used for Dependent Variable response filtering.
Output File | data/LCA/Monte_Carlo_Output.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | --- 
Photovoltaic > Efficiency > Value | PV efficiency (%) | value | Base; 0.4 | 0 | PV module efficiency uncertainty range.
Battery > Energy density (kWh/kg) > Value | kWh / kg(Battery) | value | 0.1; 0.2 | 1 | Battery specific energy uncertainty range.
Reverse Osmosis > Recovery Rate > Value | Reverse osmosis recovery rate | value | 0.4; 0.9 | 2 | Reverse osmosis recovery range.
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.025 | 3 | Same Monte Carlo range convention as other PV_E files.

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
distance_histogram | plot_distance_histogram | {'show': True, 'xlabel': True, 'save': True, 'pdf': True, 'image_kwargs': {'path': 'pyH2A.Other~PV_E_Clipart.png'}}
colored_scatter | plot_colored_scatter | Arguments - MC Analysis - colored_scatter
target_parameters | plot_target_parameters_by_distance | {'show': True}

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

# Optimization_Analysis - Deactivate

Name | Value
--- | ---
Algorithm | differential_evolution
Target | dcf.h2_cost
Direction | minimize

# Parameters - Optimization_Analysis

Parameter | Bounds
--- | ---
Photovoltaic > Nominal Power (kW) > Value | 0.1; 10
Electrolyzer > Nominal Power (kW) > Value | 4,000; 6,000
Electrolysis Using Stored Power > Fraction of stored power used for electrolysis > Value | 0; 1
Battery > Design Capacity (kWh) > Value | 0; 100,000




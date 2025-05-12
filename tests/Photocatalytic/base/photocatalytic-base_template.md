# Workflow

Parameter | Type | Position | Description
--- | --- | --- | ---
[...] | plugin, optional | int, optional | n/a
Energy.HourlyIrradiationPlugin | plugin | 0 | Plugin to calculate solar irradiation from typical meteorological year data
Hydrogen.PhotocatalyticPlugin | plugin | 2 | Computes number of required baggies, cost of baggies and catalyst cost
Hydrogen.CatalystSeparationPlugin | plugin | 2 | Computes cost of catalyst separation
Background.MultipleModulesPlugin | plugin | 3 | Modelling of multiple plant modules, adjustment of labor requirement

# Construction

Parameter | Value | Full Name
--- | --- | ---
[...] | float | n/a
capital perc 1st | 1.0 | % of Capital Spent in 1st Year of Construction

# Technical Operating Parameters and Specifications

Parameter | Value | Path | Full Name
--- | --- | --- | ---
New Plant Design Capacity (kg of H2/day) | float, optional | n/a | n/a
Scaling Ratio | float, optional | n/a | n/a
Capital Scaling Exponent | float, optional | n/a | n/a
Labor Scaling Exponent | float, optional | n/a | n/a
Operating Capacity Factor (%) | 0.9 | n/a | n/a
Plant Design Capacity (kg of H2/day) | 1111 | n/a | n/a
Maximum Output at Gate | 0.9 | Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | % of plant design capacity, reduction due to loss in H2/O2 separation.
Plant Modules | 10 | None | 10 identical modules, only affects labor requirement calculation.

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
Industrial Electricity | pyH2A.Lookup_Tables.Utility_Cost~Industrial_Electricity_AEO_2017_Reference_Case.csv | 3.29 | 0.0036 | n/a | n/a | kWh/kg H2 | GJ | GJ/kWh | Electricity usage based on Pinaud 2013.
Process Water | 0.0023749510945008 | 2.637 | 1.0 | n/a | n/a | gal/kg H2 | $(2016)/gal | None | Seawater reverse osmosis cost ca. 0.6 $/m3 (equal to ca. 0.0023 $/gal), based on Kibria 2021 and Driess 2021.

# [...] Other Variable Operating Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Sensitivity_Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
[...] | str | str | str
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH efficiency | value | 1%; 4%
Catalyst > Cost per kg ($) > Value | Catalyst cost (\$/kg) | value | 1500; 6000
Catalyst > Lifetime (years) > Value | Catalyst lifetime (years) | value | 0.25; 1
Catalyst > Concentration (g/L) > Value | Catalyst concentration (g/L) | value | 0.25; 1.0
Direct Capital Costs - Gas Processing > Compressor ($) > Value | Compressor cost (\$) | value | 250,000; 1,000,000

# Display Parameters

Parameter | Value
--- | ---
Name | PC
Color | darkgreen

# Hourly Irradiation

Parameter | Value | Comment
--- | --- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv | Location: Dagget, CA, USA

# Irradiance Area Parameters

Parameter | Value | Comment
--- | --- | ---
Module Tilt (degrees) | 0 | Flat baggies on the ground.
Array Azimuth (degrees) | 0 | Flat baggies on the ground.
Nominal Operating Temperature (Celsius) | 45 | n/a
Mismatch Derating | 0.98 | n/a
Dirt Derating | 0.98 | Values taken from Chang 2020, analogues to silicon PV.
Temperature Coefficient (per Celsius) | 0.0 | No decrease on photocatalyst activity with higher temperature assumed.

# Solar Input

Parameter | Value | Comment
--- | --- | ---
Mean solar input (kWh/m2/day) | Hourly Irradiation > Mean solar input no tracking (kWh/m2/day) > Value | Solar irradiation for baggies on flat ground without tracking.
Hourly (kWh/m2) | Hourly Irradiation > No Tracking (kW) > Value | n/a

# Solar-to-Hydrogen Efficiency

Parameter | Value | Comment
--- | --- | ---
STH (%) | 0.02 | Kang 2015, C3N4/CDot catalyst, 2% STH.

# Catalyst

Parameter | Value | Comment
--- | --- | ---
Cost per kg ($) | 3000 | CatCost Model of Urea/Melamine derived catalyst, 5% mass yield, 0.5% wt% Ruthenium as cost placeholder for CDots (Kang 2015 uses 0.48% wt% CDots on C3N4), 60 kWh electricity per kg(catalyst) due to electrochemical CDot synthesis, process template "Metal on Metal Oxide - Strong Electrostatic Adsorption" used in CatCost Model, 5 t/a production scale, estimated cost: 890 $/kg, increased to 3,000 $/kg.
Concentration (g/L) | 0.533 | Kang 2015: 2% STH, 80 mg C3N4/CDot catalyst in 150 ml, 1150 umol H2 after 6h, 9 cm^2 irradiation area (2266 J/h incident irradiation), ca. 2.395 mmol H2/h/g; Tremblay 2020: 3.4% STH (200 W m^-2), 30 mg C3N4 + catalase in 20 ml, 47.49 umol H2/h, ca. 1.583 mmol H<sub>2</sub>/h/g (ca. 5 cm<sup>2</sup> irradiation area gives reported STH); Zhao 2021: 1.16% STH (100 mW/cm^2), 0.64 cm^2 irradiated area, 11.25 umol H2 h^-1, 40 mg catalyst, 0.281 mmol H2/g/h, activity 420 nm irradiation: 65 umol H2/h, 40 mg, 1.625 mmol H2/g/h
Lifetime (years) | 0.5 | Kang 2015, 45 days continuous irradiation, 200 days with recycling
Molar Weight (g/mol) | 500 | Assumption for calculation of hypothetical homogeneous water splitting catalyst.
Molar Attenuation Coefficient (M^-1 cm^-1) | 8000 | Assumption for calculation of hypothetical homogeneous water splitting catalyst.

# Reactor Baggies

Parameter | Value | Comment
--- | --- | ---
Height (m) | 0.05 | Optimal height depends on absorption coefficient of material/complex and catalytic activity (TOF or mol H2/h/g). Height of 5 cm based on experimental set-up used in Kang 2015 (shown in Kang 2015 SI).
Length (m) | 323.0 | Baggie parameters based on Pinaud 2013.
Width (m) | 12.2 | n/a
Cost Material Top ($/m2) | 0.54 | n/a
Cost Material Bottom ($/m2) | 0.47 | n/a
Number of ports | 12 | Number of ports per baggie.
Cost of port ($) | 30 | Cost per port.
Other Costs ($) | 610.7 | Other costs per baggie.
Markup factor | 1.5 | Markup factor of baggies.
Additional land area (%) | 0.3 | Land area required in addition to area occupied by baggies.
Lifetime (years) | 5 | Lifetime of reactor baggies.

# Catalyst Separation

Parameter | Value | Comment
--- | --- | ---
Filtration cost ($/m3) | 0.24 | Cost of nanofiltration per m3 of water based on Costa 2006. Nanofiltration as a proxy for cost of actual catalyst separation.

# Direct Capital Costs - Equipment

Parameter | Value | Path | Comment
--- | --- | --- | ---
Baggie roll system ($) | 37000.0 | None | Equipment costs based on Pinaud 2013.
Forklift ($) | 18571.0 | n/a | n/a
Water pump ($) | 213.0 | n/a | n/a
Water pipes ($ per baggie) | 39.9 | Reactor Baggies > Number > Value | n/a

# Direct Capital Costs - Gas Processing

Parameter | Value | Path | Comment
--- | --- | --- | ---
Compressor ($) | 526302.0 | None | Cost estimate based on Pinaud 2013. Fixed cost of compressor for plant design output (1 ton H2/day).
Condenser ($) | 13765.0 | n/a | n/a
Intercooler-1 ($) | 15103.0 | n/a | n/a
Intercooler-2 ($) | 15552.0 | n/a | n/a
Pressure Swing Adsorption ($) | 107147.0 | n/a | n/a
Reactor Outlet Pipe ($ per baggie) | 3.17 | Reactor Baggies > Number > Value | n/a
Main Collection Pipe ($ per baggie) | 329.6 | Reactor Baggies > Number > Value | n/a
Final Collection Pipe ($ per baggie) | 23.7 | Reactor Baggies > Number > Value | n/a

# Direct Capital Costs - Control System

Parameter | Path | Value | Comment
--- | --- | --- | ---
PLC ($) | None | 2000.0 | Control system cost based on Pinaud 2013
Control Room Building ($) | None | 8000.0 | n/a
Control Room Wiring Panel ($) | None | 3000.0 | n/a
Bed Wiring Panel ($ per baggie) | Reactor Baggies > Number > Value | 146.0 | n/a
Computer and Monitor ($) | None | 1500.0 | n/a
Labview Software ($) | None | 4299.0 | n/a
Water Level Controllers ($ per baggie) | Reactor Baggies > Number > Value | 50.0 | n/a
Pressure Sensors ($ per baggie) | Reactor Baggies > Number > Value | 345.0 | n/a
Hydrogen Area Sensors ($ per baggie) | Reactor Baggies > Number > Value | 7600.0 | n/a
Gas Flow Meter ($) | None | 5500.0 | n/a
Instrument Wiring ($ per baggie) | Reactor Baggies > Number > Value | 22.7 | n/a
Power Wiring ($ per baggie) | Reactor Baggies > Number > Value | 7.6 | n/a
Conduit ($ per baggie) | Reactor Baggies > Number > Value | 142.4 | n/a

# Direct Capital Costs - Installation Costs

Parameter | Path | Value | Comment
--- | --- | --- | ---
Excavation ($ per baggie) | Reactor Baggies > Number > Value | 2570.0 | Installation costs based on Pinaud 2013.
Baggie Reactor Startup (% of baggie cost) | Direct Capital Costs - Reactor Baggies > Baggie Cost ($) > Value | 0.05 | n/a
Baggies installation ($ per baggie) | Reactor Baggies > Number > Value | 800.0 | n/a
Gas processing installation (% of gas processing cost) | Direct Capital Costs - Gas Processing > Summed Total > Value | 0.3 | n/a
Control system installation (% of control system cost) | Direct Capital Costs - Control System > Summed Total > Value | 0.3 | n/a

# Indirect Capital Costs

Parameter | Path | Value | Comment
--- | --- | --- | ---
Engineering and Design (% of total direct capital costs) | Direct Capital Costs > Total > Value | 0.07 | Indirect capital costs based on Pinaud 2013.
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
area | Area per staff (m2) | 405000 | Labor cost based on Pinaud 2013, solar collection area that can be overseen by one staff member.
supervisor | Shift supervisor | 1 | Number of shift supervisors.
shifts | Shifts | 3 | Number of shifts per day.
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0 | n/a

# Other Fixed Operating Costs

Parameter | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
g&a | G&A rate (% of labor cost) | Fixed Operating Costs > Labor Cost > Value | 0.2 | Other fixed operating costs based on Pinaud 2013.
property tax | Property tax and insurance rate (% of total capital investment per year) | Total Capital Costs > Inflated > Value | 0.02 | n/a
repairs | Production Maintenance and Repairs (% of direct capital costs) | Direct Capital Costs > Total > Value | 0.005 | n/a
fees | Licensing, Permits and Fees ($ per year) | None | 1000.0 | n/a

# Unplanned Replacement

Parameter | Full Name | Path | Value | Comment
--- | --- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.005 | Based on Pinaud 2013.

# Monte_Carlo_Analysis - Deactivate

Parameter | Value | Comment
--- | --- | ---
Samples | 50000 | Number of samples in Monte Carlo simlulation.
Target Price Range ($) | 1.5; 1.6 | n/a
Input File | tests.Photocatalytic.Base~Monte_Carlo_Output.csv | n/a

# Parameters - Monte_Carlo_Analysis - Deactivate

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH efficiency | value | 20%; Base | 0 | Maximum theoretical STH efficiency ca. 28% for two-absorber system, Schneidewind 2021.
Catalyst > Concentration (g/L) > Value | g(Catalyst) / L | value | Base; 0.01 | 1 | Model calculation for homogeneous photocatalyst: molar mass 500 g/mol, molar attenuation coefficient of 10,000 M^-1 cm^-1, water heigt of 5 cm, at a concentration of 0.01 g/L gives an absorbance of 1 (10% transmittance).
Catalyst > Cost per kg ($) > Value | \$ / kg(Catalyst) | value | 100.0; Base | 2 | CatCost model catalyst cost drops to 140 $/kg at 100 t/a production scale, estimating lower bound of catalyst cost at 100 $/kg.
Catalyst > Lifetime (years) > Value | Catalyst lifetime (years) | value | Base; 1 | 3 | Doubling lifetime of 6 months to 1 year.

# Cost_Contributions_Analysis - Deactivate

Parameter
---

# Methods - Cost_Contributions_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot', 'show': False, 'save': False}
cost_breakdown_plot_capital | cost_breakdown_plot | {'name': 'Cost_Breakdown_Plot_Capital', 'show': False, 'save': False, 'plugin': 'Finance.CapitalCostPlugin', 'plugin_property': 'direct_contributions'}

# Methods - Monte_Carlo_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
distance_cost_relationship | plot_distance_cost_relationship | Arguments - MC Analysis - distance_cost
distance_histogram | plot_distance_histogram | {'show': False, 'xlabel': True, 'save': False, 'pdf': True, 'image_kwargs': {'path': 'pyH2A.Other~Photocatalytic_Clipart.png'}}
colored_scatter | plot_colored_scatter | Arguments - MC Analysis - colored_scatter
complete_histogram | plot_complete_histogram | {'show': False, 'bins': 300}

# Arguments - MC Analysis - colored_scatter

Parameter | Value
--- | ---
show | False
save | False
pdf | False
dpi | 500
base_string | Base
title_string | Target cost range:
plot_kwargs | {'left': 0.31, 'right': 0.94, 'bottom': 0.13, 'top': 0.92, 'fig_width': 6.5, 'fig_height': 4.0}
image_kwargs | {'x': -0.4, 'zoom': 0.09, 'y': 0.5, 'path': 'pyH2A.Other~Photocatalytic_Clipart.png'}

# Arguments - MC Analysis - distance_cost

Parameter | Value
--- | ---
legend_loc | upper right
log_scale | True
plot_kwargs | {'show': False, 'save': False, 'dpi': 300, 'left': 0.09, 'right': 0.5, 'bottom': 0.15, 'top': 0.95, 'fig_width': 9, 'fig_height': 3.5}
table_kwargs | {'ypos': 0.5, 'xpos': 1.05, 'height': 0.5}
image_kwargs | {'path': 'pyH2A.Other~Photocatalytic_Clipart.png', 'x': 1.6, 'zoom': 0.095, 'y': 0.2}

# Comparative_MC_Analysis - Deactivate

Parameter | Value | Image
--- | --- | ---
pec | pyH2A.Example~210511_Future_PEC_Type_4.md | pyH2A.Other~PEC_Clipart.png
photocatalytic | pyH2A.Example~211109_Future_PEC_Type_1_Figure_Test.md | pyH2A.Other~Photocatalytic_Clipart.png
pv_e | pyH2A.Example~210613_PV_E.md | pyH2A.Other~PV_E_Clipart.png

# Methods - Comparative_MC_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
comparative_distance_histogram | plot_comparative_distance_histogram | {'show': False, 'save': False, 'pdf': True}
comparative_distance_cost_relationship | plot_comparative_distance_cost_relationship | {'show': False, 'save': False, 'dist_kwargs': {'log_scale': True}}
comparative_distance_combined | plot_combined_distance | {'show': False, 'save': False, 'left': 0.06, 'fig_width': 13, 'dist_kwargs': {'legend_loc': 'upper right', 'log_scale': True}, 'table_kwargs': {'colWidths': [0.65, 0.25, 0.12, 0.25]}, 'hist_kwargs': {'title_string': 'Target price range:'}}

# Waterfall_Analysis - Deactivate

Parameter | Name | Type | Value | Show Percent
--- | --- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 0.1 | True
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 5.0 | n/a
Catalyst > Concentration (g/L) > Value | Catalyst Concentration (g/L) | value | 0.0105 | n/a
Catalyst > Cost per kg ($) > Value | Catalyst Cost ($/kg) | value | 304.0 | n/a

# Methods - Waterfall_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
waterfall_chart | plot_waterfall_chart | {'show': False}

# Methods - Sensitivity_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | {'show': False, 'save': False, 'fig_width': 8, 'label_offset': 0.12, 'lim_extra': 0.25}


# Workflow

Name | Type | Description | Position
--- | --- | --- | ---
Hourly_Irradiation_Plugin | plugin | Plugin to calculate solar irradiation from typical meteorological year data | 0
Photocatalytic_Plugin | plugin | Computes number of required baggies, cost of baggies and catalyst cost | 2
Multiple_Modules_Plugin | plugin | Modelling of module plant modules, adjustment of labor requirement | 3

# Display Parameters

Name | Value
--- | ---
Name | Photocatalytic
Color | darkgreen

# Technical Operating Parameters and Specifications

Name | Value | Path | Full Name
--- | --- | --- | ---
Operating Capacity Factor (%) | 90.0%
Plant Design Capacity (kg of H2/day) | 1,111
Maximum Output at Gate | 90% | Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | % of plant design capacity
Plant Modules | 10

# Financial Input Values

Name | Full Name | Value | Path
--- | --- | --- | ---
basis year | Basis year | 2005
current year capital costs | Current year for capital costs | 2005
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# Hourly Irradiation

Name | Value | Comment
--- | --- | ---
File | ../Lookup_Tables/tmy_34.859_-116.889_2006_2015.csv | Dagget, CA, USA

# Irradiance Area Parameters

Name | Value | Comment
--- | --- | ---
Module Tilt (degrees) | 0
Array Azimuth (degrees) | 0
Nominal Operating Temperature (Celcius) | 45
Mismatch Derating | 98%
Dirt Derating | 98% | Values taken from Chang 2020, analogues to silicon PV
Temperature Coefficienct (per Celcius) | 0.0%

# Solar Input

Name | Value 
--- | ---
Mean solar input (kWh/m2/day) | Hourly Irradiation > Mean solar input no tracking (kWh/m2/day) > Value
Hourly (kWh/m2) | Hourly Irradiation > No Tracking (kW) > Value

# Solar-to-Hydrogen Efficiency

Name | Value | Comment
--- | --- | ---
STH (%) | 2.0% | Kang 2015, C3N4/CDot catalyst 2% STH

# Catalyst

Name | Value | Comment
--- | --- | ---
Cost per kg ($) | 3,000.0 
Concentration (kg/L) | 533.0e-6 | Kang 2015: 2% STH, 80 mg C3N4/CDot catalyst in 150 ml, 1150 umol H2 after 6h, 9 cm^2 irradiation area (2266 J/h incident irradiation), ca. 2.395 mmol H2/h/g; Tremblay 2020: 3.4% STH (200 W m^-2), 30 mg C3N4 + catalase in 20 ml, 47.49 umol H2/h, ca. 1.583 mmol H<sub>2</sub>/h/g (ca. 5 cm<sup>2</sup> irradiation area gives reported STH); Zhao 2021: 1.16% STH (100 mW/cm^2), 0.64 cm^2 irradiated area, 11.25 umol H2 h^-1, 40 mg catalyst, 0.281 mmol H2/g/h, activity 420 nm irradiation: 65 umol H2/h, 40 mg, 1.625 mmol H2/g/h
Lifetime (years) | 0.5 | Kang 2015, 45 days continous irradiation, 200 days with recycling
Molar Weight (g/mol) | 500 | Assumption for calculation of hypothetical homogeneous water splitting catalyst
Molar Attenuation Coefficient (M^-1 cm^-1) | 8000 | Assumption for calculation of hypothetical homogeneous water splitting catalyst

# Reactor Baggies

Name | Value | Comment
--- | --- | ---
Height (m) | 0.05 | Optimal height depends on absorption coefficient of material/complex and catalytic activity (TOF or mol H2/h/g)
Length (m) | 323.0
Width (m) | 12.2
Cost Material Top ($/m2) | 0.54
Cost Material Bottom ($/m2) | 0.47
Number of ports | 12
Cost of port ($) | 30
Other Costs ($) | 610.7
Markup factor | 1.5
Additional land area (%) | 30.0%
Lifetime (years) | 5

# Direct Capital Costs - Equipment

Name | Value | Path
--- | --- | ---
Baggie roll system ($) | 37,000.0
Forklift ($) | 18,571.0
Water pump ($) | 213.0
Water pipes ($ per baggie) | 39.9 | Reactor Baggies > Number > Value

# Direct Capital Costs - Gas Processing

Name | Value | Path
--- | --- | ---
Compressor ($) | 526,302.0
Condenser ($) | 13,765.0
Intercooler-1 ($) | 15,103.0
Intercooler-2 ($) | 15,552.0
Pressure Swing Adsorption ($) | 107,147.0
Reactor Outlet Pipe ($ per baggie) | 3.17 | Reactor Baggies > Number > Value
Main Collection Pipe ($ per baggie) | 329.6 | Reactor Baggies > Number > Value
Final Collection Pipe ($ per baggie) | 23.7 | Reactor Baggies > Number > Value

# Direct Capital Costs - Control System

Name | Path | Value
--- | --- | ---
PLC ($) | None | 2,000.0
Control Room Building ($) | None | 8,000.0
Control Room Wiring Panel ($) | None | 3,000.0
Bed Wiring Panel ($ per baggie) | Reactor Baggies > Number > Value | 146.0
Computer and Monitor ($) | None | 1,500.0
Labview Software ($) | None | 4,299.0
Water Level Controllers ($ per baggie) | Reactor Baggies > Number > Value | 50.0
Pressure Sensors ($ per baggie) | Reactor Baggies > Number > Value | 345.0
Hydrogen Area Sensors ($ per baggie) | Reactor Baggies > Number > Value | 7,600.0
Gas Flow Meter ($) | None | 5,500.0
Instrument Wiring ($ per baggie) | Reactor Baggies > Number > Value | 22.7
Power Wiring ($ per baggie) | Reactor Baggies > Number > Value | 7.6
Conduit ($ per baggie) | Reactor Baggies > Number > Value | 142.4

# Direct Capital Costs - Installation Costs

Name | Path | Value
--- | --- | ---
Excavation ($ per baggie) | Reactor Baggies > Number > Value | 2570.0
Baggie Reactor Startup (% of baggie cost) | Direct Capital Costs - Reactor Baggies > Baggie Cost ($) > Value | 5%
Baggies installation ($ per baggie) | Reactor Baggies > Number > Value | 800.0
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
area | Area per staff (m2) | 405,000
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
--- | --- | --- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 3.29 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 2.637 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

# Unplanned Replacement

Name | Full Name | Path | Value
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | Depreciable Capital Costs > Inflated > Value | 0.5%

# Cost_Contributions_Analysis

# Methods - Cost_Contributions_Analysis

Name | Method Name | Arguments | Values
--- | --- | --- | ---
cost_breakdown_plot_total | cost_breakdown_plot | name; show; save; pdf | Cost_Breakdown_Plot; False; True; False
cost_breakdown_plot_capital | cost_breakdown_plot | name; show; data; plugin_property; save | Cost_Breakdown_Plot_Capital; False; Capital_Cost_Plugin; direct_contributions; False

# Sensitivity_Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H_{2}/day) | value | 1200; 950
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | value | 86%; 95%
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 1%; 3%
Catalyst > Cost per kg ($) > Value | Catalyst Cost | factor | 0.1; 2
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 0.3; 10 
Other Fixed Operating Costs > repairs > Value | Repair Costs | factor | 70%; 130%

# Methods - Sensitivity_Analysis

Name | Method Name | Arguments | Values
--- | --- | --- | ---
sensitivity_box_plot | sensitivity_box_plot | show; save | False; True

# Waterfall_Analysis

Parameter | Name | Type | Value | Show Percent
--- | --- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 10% | True
Catalyst > Lifetime (years) > Value | Catalyst Lifetime (years) | value | 5.0
Catalyst > Concentration (kg/L) > Value | Catalyst Concentration (kg/L) | value | 1.05e-5
Catalyst > Cost per kg ($) > Value | Catalyst Cost ($/kg) | value | 304.0

# Methods - Waterfall_Analysis

Name | Method Name | Arguments | Values
--- | --- | --- | ---
waterfall_chart | waterfall_chart | show; save; pdf | False; True; False

# Monte_Carlo_Analysis

Name | Value | Arguments
--- | --- | ---
Samples | 50000
Target Price Range ($) | 1.5; 1.54
Output File | ../Output/210613_Future_PEC_Type_1/Monte_Carlo.csv
Input File | ../Output/210613_Future_PEC_Type_1/Monte_Carlo.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index
--- | --- | --- | --- | ---
Solar-to-Hydrogen Efficiency > STH (%) > Value | STH Efficiency | value | 20%; Base | 0
Catalyst > Cost per kg ($) > Value | \$ / kg(Catalyst) | value | 100.0; Base | 2
Catalyst > Concentration (kg/L) > Value | kg(Catalyst) / L | Value | Base; 10.0e-6 | 1
Catalyst > Lifetime (years) > Value | Catalyst Lifetime / years | value | Base; 1 | 3

# Methods - Monte_Carlo_Analysis

Name | Method Name | Arguments | Values
--- | --- | --- | ---
distance_histogram | plot_distance_histogram | show; xlabel; image; save; pdf | True; True; ../Other/Photocatalytic_Clipart.png; False; True
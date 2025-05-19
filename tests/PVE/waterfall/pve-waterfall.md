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

Name | Value
--- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv

# Irradiance Area Parameters

Name | Value 
--- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value
Array Azimuth (degrees) | 180
Nominal Operating Temperature (Celsius) | 45
Mismatch Derating | 0.98
Dirt Derating | 0.98
Temperature Coefficient (per Celsius) | -0.4%

# Irradiation Used

Name | Value
--- | ---
Data | Hourly Irradiation > No Tracking (kW) > Value

# Technical Operating Parameters and Specifications

Name | Value
--- | ---
Operating Capacity Factor (%) | 90.0%
Plant Design Capacity (kg of H2/day) | 1,000
Plant Modules | 10

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# CAPEX Multiplier

Name | Value | Full Name
--- | --- | ---
Multiplier | 1.0 | CAPEX multiplier for every 10-fold increase of system size

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

# Direct Capital Costs - PV

Name | Value | Path
--- | --- | ---
PV CAPEX ($/kW) | 1,200.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value

# Direct Capital Costs - Electrolyzer

Name | Value | Path
--- | --- | ---
Electrolyzer CAPEX ($/kW) | 1,115.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value

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

Name | Value | Path
--- | --- | ---
Electrolyzer OPEX (% of CAPEX) | 2% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value
PV OPEX (% of CAPEX) | 2% | Direct Capital Costs - PV > PV CAPEX ($/kW) > Value

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Path | Usage Path
--- | --- | --- | --- | --- | --- | --- | --- | ---
Process Water | 10 | L/kg H2 | 0.0021 | $/L | 1. | None

# Grid Electricity

Name | Value
--- | ---
Cost ($/kWh) | 10000.12

# Planned Replacement

Name | Cost ($) | Path
--- | --- | ---
Electrolyzer Stack Replacement | 40% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value

# WaterfallAnalysis

Parameter | Name | Type | Value | Show Percent
--- | --- | --- | --- | ---
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$)/ kWh(Electricity) | value | 0.025
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$/kW(PV) | value | 220
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$/kW(Electro- lyzer) | value | 200
Planned Replacement > Electrolyzer Stack Replacement > Cost ($)| Stack replacement (%E-CAPEX) | value | 20% | True

# Methods - WaterfallAnalysis

Name | Method Name | Arguments
--- | --- | ---
waterfall_chart | plot_waterfall_chart | {'show': False}
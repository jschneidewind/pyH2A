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
capital perc 1st | 1.0 | % of Capital Spent in 1st Year of Construction

# Electrolyzer

Parameter | Value
--- | ---
Yearly Operation Data | nd.array
H2 Production (yearly, kg) | nd.array
Nominal Power (kW) | 5500.0
CAPEX Reference Power (kW) | 1000.0
Power requirement increase per year | 0.01
Minimum capacity | 0.1
Conversion efficiency (kg H2/kWh) | 0.02
Replacement time (h) | 40000.0

# Technical Operating Parameters and Specifications

Parameter | Value
--- | ---
Maximum Output at Gate | float, optional
New Plant Design Capacity (kg of H2/day) | float, optional
Scaling Ratio | float, optional
Capital Scaling Exponent | float, optional
Labor Scaling Exponent | float, optional
Operating Capacity Factor (%) | 0.9
Plant Design Capacity (kg of H2/day) | 1000
Plant Modules | 10

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

Parameter | Frequency (years) | Cost ($) | Path
--- | --- | --- | ---
[...] | float | float | n/a
Electrolyzer Stack Replacement | n/a | 0.4 | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value

# [...] Unplanned Replacement [...]

Parameter | Value
--- | ---
[...] | float

# [...] Other Fixed Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Utilities

Parameter | Cost | Usage per kg H2 | Price Conversion Factor | Path | Usage Path | Usage Unit | Cost Unit | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | --- | --- | ---
[...] | float, ndarray or str | float | float | str, optional | str, optional | n/a | n/a | n/a
Process Water | 0.0021 | 10 | 1.0 | n/a | n/a | L/kg H2 | $/L | None

# [...] Other Variable Operating Operating Cost [...]

Parameter | Value
--- | ---
[...] | float

# Monte_Carlo_Analysis

Parameter | Value
--- | ---
Input File | str, optional
Samples | 100
Target Price Range ($) | 30; 50
Output File | tests/PVE/monte_carlo/Results/PV_E_Monte_Carlo.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index
--- | --- | --- | --- | ---
[...] | str | str | str | int, optional
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 200 | 0
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.029 | 2

# Display Parameters

Parameter | Value
--- | ---
Name | PV + E
Color | darkblue

# Hourly Irradiation

Parameter | Value
--- | ---
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv

# Irradiance Area Parameters

Parameter | Value
--- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value
Array Azimuth (degrees) | 180
Nominal Operating Temperature (Celsius) | 45
Mismatch Derating | 0.98
Dirt Derating | 0.98
Temperature Coefficient (per Celsius) | -0.004

# Irradiation Used

Parameter | Value
--- | ---
Data | Hourly Irradiation > No Tracking (kW) > Value

# Financial Input Values

Parameter | Full Name | Value
--- | --- | ---
equity | % Equity Financing | 0.4
interest | Interest rate on debt (%) | 0.037000000000000005

# CAPEX Multiplier

Parameter | Value | Full Name
--- | --- | ---
Multiplier | 1.0 | CAPEX multiplier for every 10-fold increase of system size

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

# Direct Capital Costs - PV

Parameter | Value | Path
--- | --- | ---
PV CAPEX ($/kW) | 1200.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value

# Direct Capital Costs - Electrolyzer

Parameter | Value | Path
--- | --- | ---
Electrolyzer CAPEX ($/kW) | 1115.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value

# Non-Depreciable Capital Costs

Parameter | Value
--- | ---
Cost of land ($ per acre) | 500.0

# Fixed Operating Costs

Parameter | Full Name | Value
--- | --- | ---
area | Area per staff (m2) | 405000
supervisor | Shift supervisor | 1
shifts | Shifts | 3
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Parameter | Value | Path
--- | --- | ---
Electrolyzer OPEX (% of CAPEX) | 0.02 | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value
PV OPEX (% of CAPEX) | 0.02 | Direct Capital Costs - PV > PV CAPEX ($/kW) > Value

# Grid Electricity

Parameter | Value
--- | ---
Cost ($/kWh) | 10000.12

# Methods - Monte_Carlo_Analysis

Parameter | Method Name | Arguments
--- | --- | ---
distance_histogram | plot_distance_histogram | {'show': False}
distance_cost_relationship | plot_distance_cost_relationship | {'show': True}


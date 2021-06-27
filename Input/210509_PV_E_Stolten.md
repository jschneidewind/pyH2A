# Workflow

Name | Type | Position
--- | --- | ---
Hourly_Irradiation_Plugin | plugin | 0
Photovoltaic_Plugin | plugin | 0

# Display Parameters

Name | Value
--- | ---
Name | PV + E (Stolten)
Color | darkblue

# Hourly Irradiation

Name | Value
--- | ---
File | ../Lookup_Tables/tmy_34.859_-116.889_2006_2015.csv

# Irradiation Used

Name | Value
--- | ---
Data | Hourly Irradiation > No Tracking (kW) > Value

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
Nominal Power (kW) | 138,000.0
CAPEX Reference Power (kW) | 1,000.0
Power requirement increase per year | 1.0%
Minimum capacity | 10.0%
Conversion efficiency (kg H2/kWh) | 0.02
Replacement time (h) | 40,000.0

# Photovoltaic

Name | Value | Path
--- | --- | ---
Nominal Power (kW) | 1.5 | Electrolyzer > Nominal Power (kW) > Value
CAPEX Reference Power (kW) | 1,000.0
Power loss per year | 0.5%

# Irradiance Area Parameters

Name | Value 
--- | ---
Module Tilt (degrees) | Hourly Irradiation > Latitude > Value
Array Azimuth (degrees) | 180
Nominal Operating Temperature (Celcius) | 45
Mismatch Derating | 0.98
Dirt Derating | 0.98
Temperature Coefficienct (per Celcius) | -0.4%

# Direct Capital Costs - PV

Name | Value | Path
--- | --- | ---
PV CAPEX ($/kW) | 972.0 | Photovoltaic > Nominal Power (kW) > Value ; Photovoltaic > Scaling Factor > Value

# Direct Capital Costs - Electrolyzer

Name | Value | Path
--- | --- | ---
Electrolyzer CAPEX ($/kW) | 730.0 | Electrolyzer > Nominal Power (kW) > Value ; Electrolyzer > Scaling Factor > Value

# Non-Depreciable Capital Costs

Name | Value | Path
--- | --- | ---
Cost of land ($ per acre) | 500.0 
Land required (acres) | 50.0

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Number of Staff | 0
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

# Planned Replacement

Name | Cost ($) | Path
--- | --- | ---
Electrolyzer Stack Replacement | 40% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value

# Analyss - Sensitivity_Analyss

Parameter | Name | Type | Values
--- | --- | --- | ---
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | PV CAPEX (\$/kW) | factor | 80%; 120%
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | Electrolyzer CAPEX (\$/kW) | factor | 80%; 120%

# Monte_Carlo_Analysis

Name | Value
--- | ---
Samples | 10000
Target Price Range ($) | 1.5; 1.54
Output File | ../Output/210510_PV_E_Stolten/Monte_Carlo.csv
Input File | ../Output/210510_PV_E_Stolten/Monte_Carlo.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index
--- | --- | --- | --- | ---
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | Base; 200 | 0
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | Base; 200 | 1
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | Base; 0.0285 | 2
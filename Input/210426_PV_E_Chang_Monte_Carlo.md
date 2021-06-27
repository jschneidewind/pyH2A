# Workflow

Name | Type | Position
--- | --- | ---
Photovoltaic_Plugin | plugin | 0

# Display Parameters

Name | Value
--- | ---
Name | PV + E (Chang)
Color | darkred

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
equity | % Equity Financing | 50%
interest | Interest rate on debt (%) | 5.75%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 100%

# CAPEX Multiplier

Name | Value | Full Name
--- | --- | ---
Multiplier | 0.9 | CAPEX multiplier for every 10-fold increase of system size

# Irradiation Used

Name | Value
--- | ---
Data | ../Lookup_Tables/Hourly_PV_Power_Ratio_Townsville_AUS_Chang_2020.csv

# Electrolyzer

Name | Value
--- | ---
Nominal Power (kW) | 1,000.0
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
Land required (acres) | 50.0

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Number of Staff | 0
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Value | Path
--- | --- | ---
Electrolyzer OPEX ($/kW/year) | 17.0 | Electrolyzer > Nominal Power (kW) > Value
PV OPEX ($/kW/year) | 14.4 | Photovoltaic > Nominal Power (kW) > Value

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit | Path | Usage Path
--- | --- | --- | --- | --- | --- | --- | --- | ---
Process Water | 10 | L/kg H2 | 0.0021 | $/L | 1. | None

# Planned Replacement

Name | Cost ($) | Path
--- | --- | ---
Electrolyzer Stack Replacement | 40% | Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value

# Monte_Carlo_Analysis

Name | Value
--- | ---
Samples | 10000
Target Price Range ($) | 1.5; 1.54
Output File | ../Output/210426_PV_E_Chang_MC/Monte_Carlo.csv
Input File | ../Output/210426_PV_E_Chang_MC/Monte_Carlo.csv

# Parameters - Monte_Carlo_Analysis

Parameter | Name | Type | Values | File Index
--- | --- | --- | --- | ---
Direct Capital Costs - PV > PV CAPEX ($/kW) > Value | \$ / kW(PV) | value | 1200; 200 | 0
Direct Capital Costs - Electrolyzer > Electrolyzer CAPEX ($/kW) > Value | \$ / kW(Electrolyzer) | value | 1115; 200 | 1
Electrolyzer > Conversion efficiency (kg H2/kWh) > Value | kg($H_{2}$) / kWh(Electricity) | value | 0.02; 0.03 | 2
# Workflow

Name | Type | Description
--- | --- | ---
Production_Scaling_Plugin | plugin | Computes plant output and scaling factors (if scaling is requested)
production_scaling | function | core function to process yearly plant output
Capital_Cost_Plugin | plugin | Calculation of direct, indirect and non-depreciable capital costs
initial_equity_depreciable_capital | function | core function to process depreciable capital costs
non_depreciable_capital_costs | function | core function to process non-depreciable capital costs
Replacement_Plugin | plugin | Calculation of replacement costs
replacement_costs | function | core function to process replacement costs
Fixed_Operating_Cost_Plugin | plugin | Calculation of fixed operating costs
fixed_operating_costs | function | core function to process fixed operating costs
Variable_Operating_Cost_Plugin | plugin | Calculation of variable operating costs, including utilities
variable_operating_costs | function | core function to process variable operating costs

# Technical Operating Parameters and Specifications

Name | Value | Path | Full Name
--- | --- | --- | ---
Operating Capacity Factor (%) | 97.0%
Plant Design Capacity (kg of H2/day) | 59,150

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2040
basis year | Basis year | 2016
current year capital costs | Current year for capital costs | 2016
startup time | Start-up Time (years) | 1
plant life | Plant life (years) | 40
analysis period | Analysis period (years) | 40
depreciation length | Depreciation Schedule Length (years) | 20
depreciation type | Depreciation Type | MACRS
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%
debt | Debt period | Constant
startup cost fixed | % of Fixed Operating Costs During Start-up | 75%
startup revenues | % of Revenues During Start-up | 50%
startup cost variable | % of Variable Operating Costs During Start-up | 75%
decommissioning | Decommissioning costs (% of depreciable captical investment) | 10%
salvage | Salvage value (% of total capitcal investment) | 10%
inflation | Inflation rate (%) | 1.9%
irr | After-tax Real IRR (%) | 8.0%
state tax | State Taxes (%) | 6.0%
federal tax | Federal Taxes (%) | 21.0%
working capital | Working Capital (% of yearly change in operating costs) | 15.0%

# Construction

Name | Full Name | Value
--- | --- | ---
capital perc 1st | % of Capital Spent in 1st Year of Construction | 8%
capital perc 2nd | % of Capital Spent in 2nd Year of Construction | 60%
capital perc 3rd | % of Capital Spent in 3rd Year of Construction | 32%

# Direct Capital Costs

Name | Value
--- | ---
Direct Capital Cost | 29,996,476.0

# Indirect Capital Costs

Name | Value
--- | ---
Site Preparation ($) | 599,930.0
Engineering and Design ($) | 2,999,648.0
Process Contingency ($) | 0.0
Project Contingency ($) | 4,499,471.0
Other (Depreciable) Capital ($) | 0.0
Up-Front Permitting Costs ($) | 4,499,471.0

# Non-Depreciable Capital Costs

Name | Value
--- | ---
Cost of land ($ per acre) | 50,000.0
Land required (acres) | 5

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Total plant staff (FTEs) | 10
hourly labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0

# Other Fixed Operating Costs

Name | Full Name | Value | Path
--- | --- | --- | ---
g&a | G&A rate (% of labor cost) | 20.0% | Fixed Operating Costs > Labor Cost > Value
property tax | Property tax and insurance rate (% of total capital investment per year) | 2.0% | Total Capital Costs > Inflated > Value
rent | Rent ($ per year) | 0.0 | None
fees | Licensing, Permits and Fees ($ per year) | 0.0 | None
material cost repair | Material costs for maintenance and repairs ($ per year) | 0.0 | None
repair | Production Maintenance and Repairs ($ per year) | 899,894.0 | None
other fees | Other Fees ($ per year) | 0.0 | None
other o&m | Other Fixed O&M Costs ($ per year) | 0.0 | None

# Utilities

Name | Usage per kg H2 | Usage Unit | Cost | Cost Unit | Price Conversion Factor | Price Conversion Factor Unit
--- | --- | --- | --- | --- | --- | ---
Industrial Electricity | 51.3 | kWh/kg H2 | ../Lookup_Tables/Industrial_Electricity_AEO_2017_Reference_Case.csv | GJ | 0.0036 | GJ/kWh
Process Water | 3.78 | gal/kg H2 | 0.0023749510945008 | $(2016)/gal | 1. | None

# Other Variable Operating Costs

Name | Full Name | Value
--- | --- | ---
other | Other Variable Operating Costs ($/year) | 0.0
material | Other Material Costs ($/year) | 0.0
waste | Waste Treatment Costs ($/year) | 0.0
solid waste | Solid waste disposal costs ($/year) | 0.0
royalties | Royalties ($/year) | 0.0
profit | Operator Profit ($/year) | 0.0
subsidies | Subsidies, Tax Incentives ($/year) | 0.0

# Planned Replacement

Name | Frequency (years) | Cost ($)
--- | --- | ----
Planned Replacement | 10 | 4,499,471.0

# Unplanned Replacement

Name | Full Name | Value | Path
--- | --- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | 0.5% | Depreciable Capital Costs > Inflated > Value

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Utilities > Industrial Electricity > Usage per kg H2 | Electricity Usage (kWh/kg H2) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H2/day) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | factor | 95%; 105%
Financial Input Values > irr > Value | Internal Rate of Return | factor | 95%; 105%
Utilities > Process Water > Usage per kg H2 | Water Usage per kg H2 | factor | 50%; 150%
Planned Replacement > Planned Replacement > Frequency (years) | Replacement Frequency (years) | value | 1; 15
Financial Input Values > irr > Value | Internal Rate of Return | factor | 95%; 105%
Other Variable Operating Costs > subsidies > Value | Subsidies | value | -4,500,000.0; 4,500,000.0
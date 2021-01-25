# Technical Operating Parameters and Specifications

Name | Value
--- | ---
Operating Capacity Factor (%) | 90.0%
Plant Design Capacity (kg of H2/day) | 1,000
Scaling Ratio | 1.5
Scaling Exponent | 0.78

# Financial Input Values

Name | Full Name | Value
--- | --- | ---
ref year | Reference year | 2016
startup year | Assumed start-up year | 2040
basis year | Basis year | 2005
current year capital costs | Current year for capital costs | 2010
startup time | Start-up Time (years) | 1
plant life | Plant life (years) | 40
analysis period | Analysis period (years) | 40
depreciation length | Depreciation Schedule Length (years) | 20
depreciation type | Depreciation Type | MACRS
equity | % Equity Financing | 40%
interest | Interest rate on debt (%) | 3.7%
debt | Debt period | Constant
startup cost fixed | % of Fixed Operating Costs During Start-up | 100%
startup revenues | % of Revenues During Start-up | 75%
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
capital perc 1st | % of Capital Spent in 1st Year of Construction | 20%
capital perc 2nd | % of Capital Spent in 2nd Year of Construction | 80%

# Energy Feedstocks, Utilities, and Byproducts

Name | Price Conversion Factor (GJ/kWh) | Price in Startup Year | Usage (kWh/kg H2) | Cost in Startup Year
--- | --- | --- | --- | ---
Industrial Electricity | 0.0036 | 0.077596976 | 2.01 | 37,711

# Total Capital Costs

Name | Value
--- | ---
H2A Total Direct Capital Cost | 3,237,854.0

# OR 

# Total Capital Costs

Name | Value
--- | ---
STH Scaling Capital Cost | 2,000,000.0
H2 Scaling Capital Cost | 1,237,854.0

# Indirect Depreciable Capital Costs

Name | Value
--- | ---
Site Preparation ($) | 50,009.0
Engineering and Design ($) | 125,022.0
Process Contingency ($) | 0.0
Project Contingency ($) | 500,088.0
Other (Depreciable) Capital ($) | 0.0
Up-Front Permitting Costs ($) | 187,533.0

# Non-Depreciable Capital Costs

Name | Value
--- | ---
Cost of land ($ per acre) | 5,000.0
Land required (acres) | 5   (Optional, can be set through Photocatalytic_Plugin)
Other non-depreciable capital costs ($) | 0.0

# Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
staff | Total plant staff (FTEs) | 10
labor cost | Burdened labor cost, including overhead ($ per man-hr) | 50.0
g&a | G&A rate (% of labor cost) | 20.0%
property tax | Property tax and insurance rate (% of total capital investment per year) | 2.0%

# Other Fixed Operating Costs

Name | Full Name | Value
--- | --- | ---
rent | Rent ($ per year) | 0.0
fees | Licensing, Permits and Fees ($ per year) | 0.0
material cost repair | Material costs for maintenance and repairs ($ per year) | 0.0
repair | Production Maintenance and Repairs ($ per year) | 899,894.0
other fees | Other Fees ($ per year) | 0.0
other o&m | Other Fixed O&M Costs ($ per year) | 0.0

# Materials and Byproducts

Name | $(2016)/gal | Usage per kg H2 | Cost in Startup Year ($)
--- | --- | --- | ---
Process Water | 0.0023749510945008 | 3.78 | 158,921.0

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

Name | Full Name | Value
--- | --- | ---
unplanned replacement | Total Unplanned Replacement Capital Cost Factor (% of total direct depreciable costs/year) | 0.5%

# Sensitivity Analysis

Parameter | Name | Type | Values
--- | --- | --- | ---
Energy Feedstocks, Utilities, and Byproducts > Industrial Electricity > Usage (kWh/kg H2) | Electricity Usage (kWh/kg H2) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value | Plant Design Capacity (kg H2/day) | factor | 95%; 105%
Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value | Operating Capacity Factor | factor | 95%; 105%
Financial Input Values > irr > Value | Internal Rate of Return | factor | 95%; 105%
Materials and Byproducts > Process Water > Usage per kg H2 | Water Usage per kg H2 | factor | 50%; 150%
Planned Replacement > Planned Replacement > Frequency (years) | Replacement Frequency (years) | value | 1; 15
Unplanned Replacement > unplanned replacement > Value | Unplanned Replacement Cost Fraction (%) | value | 0.3%; 0.8%
Other Variable Operating Costs > subsidies > Value | Subsidies | value | -4,500,000.0; 4,500,000.0

# Solar-to-Hydrogen Efficiency (Optional)

Name | Value
--- | ---
Base STH | 5.0%
Actual STH | 5.0%

# Catalyst

Name | Value
--- | ---
Cost per kg ($) | 419.2159841
Concentration (kg/L) | 0.003

# Reactor Baggies

Name | Value
--- | ---
Cost per baggie ($) | 4439.168639
Length (m) | 61.0
Width (m) | 6.1
Height (m) | 0.4
Additional land area (%) | 39.19138455%

# Solar Input

Name | Value
--- | ---
Mean solar input (kWh/m2/day) | 5.25

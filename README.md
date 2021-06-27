<img align="right" src="./Other/pyH2A.svg"/>

# pyH2A

pyH2A is an extensible Python implementation of the H2A Hydrogen Analysis model developed by the [U.S. Department of Energy](https://www.hydrogen.energy.gov/h2a_analysis.html)/[NREL](https://www.nrel.gov/hydrogen/h2a-production-models.html).

`pyH2A.py` invokes the basic discounted cash flow analysis functionality and it can be interfaced with different `plugins` to allow modelling of various hydrogen production technologies. Furthermore, different analysis modules can be applied, allowing for detailed analysis of the discounted cash flow results.

It is a command line tool, with the input being provided using Markdown formatted plaintext files and the output being plots and formatted PDF reports.

Note: pyH2A is currently under development and may undergo major changes in its design.

# Installation

Currently, pyH2A has to be installed by cloning the GitHub repository:

```bash
git clone https://github.com/jschneidewind/pyH2A
```

It is planned to enable `pip` installation in the future.

# Dependencies

pyH2A uses Python >3.7 with the following libraries: `NumPy` and `SciPy` as well as `Matplotlib` and `fpdf` for output generation.

# Use

Input is provided using a plaintext Markdown file, which has to follow the layout of the `Input.md` template for the most part. Input files are structured by headers (designated by '#'), which are followed by Markdown style tables. Headers and tables are parsed by `pyH2A.py` to generate dictionaries which are used for computations. Certain input sections are mandatory (such as 'Technical Operating Parameters and Specifications' or 'Financial Input Values'), while plugins can be used to process additional input sections.

pyH2A can be run in the command line using:

```bash
python pyH2A.py path/to/input_file path/to/output_directory
```

For example, if the input file `Input.md` is in the `../Input` directory and the output directory is `../Output/Example_Output`:

```bash
python pyH2A.py ../Input/Input.md ../Output/Example_Output
```

# Example output

Cost breakdown:

![cost breakdown plot](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_Future_PEC_Type_1_Limit/Cost_Breakdown_Plot.png "Cost breakdown plot")

Sensitivty analysis:

![sensitivity plot](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_Future_PEC_Type_1_Limit/Sensitivity_Box_Plot.png "Sensitivity plot")

Waterfall analysis:

![waterfall plot](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_Future_PEC_Type_1/Waterfall_Chart.png "Waterfall plot")

Monte Carlo analysis, also allowing for comparison of different production pathways:

![colored scatter](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_PV_E/Monte_Carlo_Colored_Scatter.png "Colored Scatter")

![comparative distance histograms](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_PV_E/Monte_Carlo_Comparative_Distance_Histogram.png "Comparative Distance Histogram")

![comparative distance cost relationship](https://github.com/jschneidewind/pyH2A/blob/master/Output/210627_PV_E/Monte_Carlo_Comparative_Distance_Cost_Relationship.png "Comparative Distance Cost Relationship")

A formatted PDF file combining the plots and a summary of the computed hydrogen cost:

![PDF report](https://github.com/jschneidewind/pyH2A/blob/master/Output/Future_PEC_Type_2/Future_PEC_Type_2.pdf "PDF report")

# To do

Block diagram illustrating flow of program

# License

Copyright (c) Jacob Schneidewind

All software is licensed under a MIT license (see `LICENSE` file).

Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

All other files and their contents are licensed under a
[Creative Commons Attribution 4.0 International License][cc-by]. (see `LICENSE-CC-BY`)

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
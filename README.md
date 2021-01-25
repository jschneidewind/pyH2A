# pyH2A

pyH2A is an extensible Python implementation of the H2A Hydrogen Analysis model developed buy the [U.S. Department of Energy](https://www.hydrogen.energy.gov/h2a_analysis.html)/[NREL](https://www.nrel.gov/hydrogen/h2a-production-models.html).

`pyH2A.py` provides the basic discounted cashflow analysis functionality and it can be interfaced with different `plugins` to allow modelling of various hydrogen production technologies. It is a command line tool, with the input being provided using Markdown formatted plaintext files and the output being plots and formatted PDF reports.

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

The current output is a cost breakdown plot:

![cost breakdown plot](https://github.com/jschneidewind/pyH2A/blob/master/Output/Future_PEC_Type_2/cost_breakdown.png "Cost breakdown plot")

a sensitivity analysis plot (if sensitivity analysis is requested in the input file):

![sensitivity plot](https://github.com/jschneidewind/pyH2A/blob/master/Output/Future_PEC_Type_2/sensitivity_box_plot.png "Sensitivity plot")

and a formatted PDF file combining the plots and a summary of the computed hydrogen cost.

# License

Copyright (c) Jacob Schneidewind

All software is licensed under a MIT license (see `LICENSE` file).
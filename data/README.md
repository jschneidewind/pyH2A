# Overview

This directory contains all data presented in the accompanying publication. It is structured in the following way:

Name | Description
--- | ---
custom-reference.docx | `.docx` reference file for rendering of .md files
Defaults.md | Financial input and workflow parameters shared by all models
Defaults.docx | `.docx` rendered version of Defaults.md
pyH2A_execution.py | Python script to run pyH2A calculations
PEC | Directory with data for photoelectrochemical water splitting
Photocatalytic | Directory with data for photocatalytic water splitting
PV_E | Directory with data for photovoltaic + electrolysis

Each data directory contains data for the `Base` and `Limit` case in separate sub-directories. These sub-directories contain the `.md` input file, a `.docx` rendered version of the input file, and files for the generated plots. `Base` subdirectories also contain a `.csv` file with the results of the Monte Carlo simulation.
Finally, in the `Photocatalytic` directories there are `.json` files with the CatCost model used to estimate catalyst production cost. They can be loaded in the [NREL CatCost](https://catcost.chemcatbio.org/catalyst-estimate) web app. 

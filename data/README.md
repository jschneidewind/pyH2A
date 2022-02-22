# Overview

This directory contains all data presented in the accompanying publication. It is structured in the following way:

Name | Description
--- | ---
Defaults.md | Financial input and workflow parameters shared by all models
Figures | Files for generation of specific figures
PEC | Directory with data for photoelectrochemical water splitting
Photocatalytic | Directory with data for photocatalytic water splitting
PV_E | Directory with data for photovoltaic + electrolysis
pyH2A_execution.py | Python script to run pyH2A calculations

Each data directory contains data for the `Base` and `Limit` case in separate sub-directories. These sub-directories contain the `.md` input file and files for the generated plots. `Base` subdirectories also contain a `.csv` file with the results of the Monte Carlo simulation.
`PEC` contains an additional directory with a modified process model which does not include solar concentration (`No_Conc`).
In the `Photocatalytic` directories there are `.json` files with the CatCost model used to estimate catalyst production cost. They can be loaded in the [NREL CatCost](https://catcost.chemcatbio.org/catalyst-estimate) web app. 
The `PV_E` directory contains an addtional subdirectory for analysis of historical data.
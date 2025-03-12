# HDock Output Files

This directory contains the results from HDock docking simulations, organized as follows:

## 1. Summary CSV File

A CSV file summarizing the docking results is located at the root of this directory. This file includes key metrics and scores for each docking simulation, providing a quick overview of the outcomes.

## 2. Individual Docking Result Folders

Each docking simulation has a dedicated folder named after its unique `df_download_ID`. These folders contain the detailed output files for each docking run, including:

- **Receptor PDB File**: The protein structure used as the receptor in the docking simulation.
- **Ligand PDB File**: The ligand molecule docked to the receptor.
- **HDock Output File**: Contains all predicted docking solutions, typically including thousands of potential binding modes.

For more information on interpreting these files, refer to the [HDOCK server documentation](https://academic.oup.com/nar/article-abstract/45/W1/W365/3829194).

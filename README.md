# Protein-Protein Interaction Analysis: HMOX1 and Your Protein of Interest

## Introduction

Protein-protein interactions (PPIs) are central to understanding cellular mechanisms and drug discovery. In many cases, researchers face challenges when setting up numerous docking experiments due to the scarcity of easy-to-use tools that can handle large datasets. This project was born out of the need for an efficient pipeline to perform multiple docking experiments, ultimately leading to the adoption of HDOCK as a robust docking platform.

This repository provides a comprehensive pipeline for analyzing protein-protein interactions between HMOX1 and any protein of your interest. It covers the entire workflow: from retrieving and preparing receptor and ligand structures to submitting docking jobs and analyzing the docking results.

## Project Overview

The repository is organized into several folders, each responsible for a specific stage of the workflow:

- **1_retrieve_pdbs**  
  Contains Python scripts to retrieve PDB files from online databases and generate data frames for receptors and ligands:
  - `1_generate_receptor_df.py`: Creates a receptor data frame.
  - `2_download_receptor_pdbs.py`: Downloads receptor PDBs.
  - `3_generate_ligand_df.py`: Creates a ligand data frame.
  - `4_filter_and_download_ligand_pdbs.py`: Filters and downloads ligand PDBs.

- **2_send_HTML_jobs**  
  This folder contains the Node.js scripts that submit docking jobs to the HDOCK web server. It handles the creation of HTML job requests required by the server.

- **3_hdock_responses**  
  Stores the responses from the HDOCK server after job submission. These responses are used to track and manage the docking jobs.

- **4_hdock_results**  
  Contains the results returned by HDOCK after docking simulations. These files are later processed and analyzed.

- **config**  
  Holds configuration files:
  - `config.json`: Contains various configuration settings required for the pipeline.

- **data**  
  Organized directory to store the downloaded data:
  - `hdock_output`: Contains a `README.md` with details about the output structure.
  - `ligand_pdbs`: Contains downloaded ligand PDB files.
  - `receptor_pdbs`: Contains downloaded receptor PDB files.

- **protocols_for_me**  
  Contains documentation and guidelines related to the development and version control processes:
  - `github_push.md`: Guidelines for pushing changes to GitHub.
  - `gitignore.md`: Information on ignoring specific files during version control.

- **results**  
  Contains the output of the analysis:
  - `hdock_plots`: Stores plots generated from docking results analysis.

## Workflow

1. **Retrieve PDB Files**:  
   Run scripts in the `1_retrieve_pdbs` folder to generate receptor and ligand data frames and download the corresponding PDB files.

2. **Submit Docking Jobs**:  
   Use the Node.js scripts in the `2_send_HTML_jobs` folder to send HTML-based job submissions to the HDOCK web server.

3. **Capture HDOCK Responses**:  
   Monitor the responses from HDOCK in the `3_hdock_responses` folder to track job status.

4. **Download and Analyze Results**:  
   The docking results are stored in the `4_hdock_results` folder. Analyze these results and generate visualizations saved under the `results` folder.

## Quick Start

### Prerequisites

- **Python 3.x** (recommended)
- **Node.js**
- Valid e-mail addresses for HDOCK Web Server job submissions

### Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt

# Protein-Protein Interaction Analysis: HMOX1 and Your Protein of Interest

This repository provides a pipeline for analyzing protein-protein interactions (PPI) focusing on HMOX1 and other proteins of interest. Users can extract, dock, and analyze interactions between HMOX1 and their proteins of interest with ease.

The pipeline consists of several Python and Node.js scripts, along with tools to extract receptor and ligand data, perform docking simulations using HDOCK, and analyze the results.

## Table of Contents

- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
- [Workflow](#workflow)
- [Notebooks](#notebooks)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The aim of this project is to provide an easy-to-use pipeline for protein-protein interaction analysis, focusing on HMOX1 and a user-defined protein of interest. By following this pipeline, you can:

- **Extract Receptor and Ligand Structures**: Retrieve receptor and ligand structures from online databases such as RCSB PDB and AlphaFold.
- **Docking**: Submit receptor and ligand files to the HDOCK web server for docking simulations.
- **Data Download**: Download and organize docking results for further analysis.
- **Analysis**: Analyze the docking results using provided Python scripts.

## Workflow

1. **Generate Input PDBs**: [workflow/1_generate_input_pdbs.ipynb](workflow/1_generate_input_pdbs.ipynb)  
   - This notebook generates the input PDB files for receptors and ligands, preparing them for docking.

2. **Queue HDock Jobs**: [workflow/2_queue_hdock_jobs](workflow/2_queue_hdock_jobs)  
   - This step uses a Node.js script to submit docking jobs to the HDOCK web server. Ensure you have valid email addresses for job submissions.

3. **Download HDock Results**: [workflow/3_hdock_downloader.py](workflow/3_hdock_downloader.py)  
   - This Python script downloads the docking results from the HDOCK server and organizes them for analysis.

4. **Analyze HDock Results**: [workflow/4_hdock_analysis.ipynb](workflow/4_hdock_analysis.ipynb)  
   - This notebook analyzes the docking results, providing insights into protein-protein interactions.


### Prerequisites

- Python 3.x (recommended)
- Node.js
- Available E-Mail addresses for HDOCK Web Server (for docking job submissions)

### Dependencies

Before running the pipeline, you need to install the required packages and dependencies. Follow these steps:

#### Install Python packages:
```bash
pip install -r requirements.txt

cd step_by_step_workflow/2_queue_hdock_jobs
npm install
´´´


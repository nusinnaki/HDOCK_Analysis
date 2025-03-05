Protein-Protein Interaction Analysis: HMOX1 and Your Protein of Interest
This repository provides a pipeline for analyzing protein-protein interactions (PPI) focusing on HMOX1 and other proteins of interest. Users can extract, dock, and analyze interactions between HMOX1 and their proteins of interest with ease.

The pipeline consists of several Python and Node.js scripts, along with tools to extract receptor and ligand data, perform docking simulations using HDOCK, and analyze the results.

Table of Contents
Project Overview
Installation
Quick Start
Workflow
Scripts
Contributing
License
Project Overview
The aim of this project is to provide an easy-to-use pipeline for protein-protein interaction analysis, focusing on HMOX1 and a user-defined protein of interest. By following this pipeline, you can:

Extract Receptor and Ligand Structures: Retrieve receptor and ligand structures from online databases such as RCSB PDB and AlphaFold.
Docking: Submit receptor and ligand files to the HDOCK web server for docking simulations.
Data Download: Download and organize docking results for further analysis.
Analysis: Analyze the docking results using provided Python scripts.
Installation
Prerequisites
Python 3.x (recommended)
Node.js
HDOCK Web Server Account (for docking job submissions)
Dependencies
Before running the pipeline, you need to install the required packages and dependencies. Follow these steps:

Install Python packages:

bash
Copy
Edit
pip install -r requirements.txt
Install Node.js dependencies:

Navigate to the directory containing your Node.js scripts.
Run:
bash
Copy
Edit
npm install
Quick Start
This section will walk you through the basic steps of using the pipeline.

Step 1: Extract Receptor and Ligand Files
You can extract the PDB files for your receptor (HMOX1) and protein of interest using the Python script 1_generate_input_pdbs.py.

Run the Python script to extract the receptor and ligand files:

bash
Copy
Edit
python 1_generate_input_pdbs.py
This script retrieves PDB files from the RCSB Protein Data Bank and AlphaFold based on the protein identifiers you provide.

The script will output the corresponding receptor and ligand files in the specified directory.

Step 2: Submit Jobs to HDOCK Web Server
Use the Node.js script queue_hdock_jobs.js to submit the receptor-ligand pairs for docking to the HDOCK web server.

Run the Node.js script to queue docking jobs:

bash
Copy
Edit
node queue_hdock_jobs.js
This will submit all receptor and ligand files to HDOCK for docking. Ensure you have an HDOCK account set up for job submission.

Step 3: Download Docking Results
Once the docking jobs are completed, you will receive a responses.csv containing the results.

Run the Python script hdock_downloader.py to download the results:

bash
Copy
Edit
python hdock_downloader.py
This script will fetch the docking output files and organize them in the specified folder.

Step 4: Analyze Docking Results
Once all the docking results are downloaded, use the Python script hdock_analysis.py to analyze the data.

Run the analysis script:

bash
Copy
Edit
python hdock_analysis.py
The analysis script will process the docking results, generate relevant visualizations, and provide insights into the protein-protein interactions.

Workflow
The pipeline is composed of the following steps:

Extract receptor and ligand PDB files with 1_generate_input_pdbs.py.
Submit receptor-ligand pairs to the HDOCK server using queue_hdock_jobs.js.
Download docking results using hdock_downloader.py.
Analyze docking results using hdock_analysis.py.
The pipeline can be customized to analyze any protein-protein interaction by simply changing the input proteins.

Scripts
The following scripts are included in the repository:

1_generate_input_pdbs.py
Extracts receptor and ligand structures from RCSB PDB and AlphaFold.

queue_hdock_jobs.js
Submits receptor-ligand docking jobs to the HDOCK web server.

hdock_downloader.py
Downloads the results from the HDOCK server after docking.

hdock_analysis.py
Analyzes the docking results, generates visualizations, and interprets the data.

Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request with your changes. Be sure to follow the coding style and add tests for any new features.

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -m 'Add new feature').
Push to the branch (git push origin feature-branch).
Open a pull request.
License
This project is licensed under the MIT License - see the LICENSE file for details.
# Protein-Protein Interaction Analysis: HMOX1 and Your Protein of Interest

This repository provides a pipeline for analyzing protein-protein interactions (PPI) focusing on HMOX1 and other proteins of interest. Users can extract, dock, and analyze interactions between HMOX1 and their proteins of interest with ease.

The pipeline consists of several Python and Node.js scripts, along with tools to extract receptor and ligand data, perform docking simulations using HDOCK, and analyze the results.

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Workflow](#workflow)
- [Scripts](#scripts)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The aim of this project is to provide an easy-to-use pipeline for protein-protein interaction analysis, focusing on HMOX1 and a user-defined protein of interest. By following this pipeline, you can:

- **Extract Receptor and Ligand Structures**: Retrieve receptor and ligand structures from online databases such as RCSB PDB and AlphaFold.
- **Docking**: Submit receptor and ligand files to the HDOCK web server for docking simulations.
- **Data Download**: Download and organize docking results for further analysis.
- **Analysis**: Analyze the docking results using provided Python scripts.

## Installation

### Prerequisites
- Python 3.x (recommended)
- Node.js
- Available E-Mail addresses for HDOCK Web Server (for docking job submissions)

### Dependencies

Before running the pipeline, you need to install the required packages and dependencies. Follow these steps:

#### Install Python packages:
```bash
pip install -r requirements.txt

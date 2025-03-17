# Node.js Execution Guide for HDOCK Upload Script

This guide explains how to set up and execute the Node.js scripts for uploading receptor and ligand files via HDOCK.

## Prerequisites

- **Node.js:** Ensure you have Node.js (v12 or later) installed.  
  Check your version with:
  ```bash
  node -v


## Script Overview
# File Handling
Input Directories

Receptors: ../data/receptor_pdbs/ (PDB files)

Ligands: ../data/ligand_pdbs/ (PDB files)

# File Processing

Batch processing of structure files

Supports PDB and custom AlphaFold-derived structures

## Submission Workflow
#Request Preparation

Generates POST requests for each receptor-ligand pair

Attaches files as multipart/form-data

Email rotation every 10 submissions

# Job Submission

javascript
Copy
fetch('http://hdock.phys.hust.edu.cn/submit', {
  method: 'POST',
  body: formData
});
Error handling for failed submissions

Automatic retry mechanism

# Logging & Tracking

CSV output (responses.csv) contains:

Column	Description
Timestamp	Submission time
ReceptorFile	PDB filename
LigandFile	PDB filename
HDOCK_Response	Server response text

📅 Data Retention Policy: Results automatically deleted after 14 days
📧 Support: hdock@hust.edu.cn

## Web Interface Features
# User Dashboard
html
Copy
<div class="status-board">
  <h2>Job job_id: <span class="status">QUEUED</span></h2>
  <div class="loader"></div>
  <p>Auto-refreshing in 10 seconds...</p>
</div>
Run HTML
Real-time status updates

Browser notifications

Mobile-responsive design


## New Submission
You can re-run the code. OR if you have mistakes, use the bugsfixes.py to analyse which job_IDs were problematic, and recreate your folders.


## References
# Databases & Links
Protein Data Bank (RCSB)	https://www.rcsb.org
AlphaFold DB	https://alphafold.ebi.ac.uk
HDOCK Server	http://hdock.phys.hust.edu.cn
Node.js Docs	https://nodejs.org/en/docs
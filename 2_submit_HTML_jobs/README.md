Node.js Execution Guide for HDOCK Upload Script
This guide explains how to set up and execute the Node.js scripts for uploading receptor and ligand files via HDOCK, with separate sections for file handling and script handling.

Prerequisites
Node.js: Ensure you have Node.js (v12 or later) installed.
Check your version with:
bash
Copy
node -v
Dependencies: Make sure you have installed required Node.js packages (axios, form-data, etc.). You can install them via npm:
bash
Copy
npm install axios form-data
Script Overview
File Handling
Input Directories:

Receptors: Files are expected in the directory:
../data/receptor_pdbs/
(Only PDB files are processed)

Ligands: Files are expected in the directory:
../data/ligand_pdbs/
(Only PDB files are processed)

Additional Folders for Submission Jobs:

To ensure you do not exceed the allowable job submissions relative to your email rotation limits, please create the following folders in your data directory:

submit_jobs_receptors
submit_jobs_ligands
Place the appropriate receptor and ligand files for submission inside these folders. This helps in segregating the files meant for job submissions from other files.

File Processing:

Batch Processing:
The script automatically processes each receptor-ligand pair, preparing the necessary POST requests.

Supported Files:
Supports both standard PDB files and custom AlphaFold-derived structure files.

Local Logging:
A CSV file (responses.csv) is generated (and updated) to record the outcome of each submission.

Script Handling
Submission Workflow:

Request Preparation:

The script generates a POST request for each receptor-ligand pair.
Files are attached as multipart/form-data.
The required email and job name are included in the submission.
Email Rotation:

An array of email addresses is provided.
The script rotates emails every 10 submissions (customizable via emailRotationInterval).
Important: If you have more jobs than allowed by the number of available emails (e.g., 100 jobs but only 9 email addresses), the HDOCK website may enforce a limit and the script might fail. Ensure that your email count and submission jobs are aligned.
Job Submission:
The code snippet for the upload (submission) is as follows:

javascript
Copy
fetch('http://hdock.phys.hust.edu.cn/runhdock.php', {
  method: 'POST',
  body: formData
});
This POST call is wrapped with error handling and an automatic retry mechanism for failed submissions.

Logging & Tracking:
The script logs each submission to a CSV file (responses.csv) which includes:

Column	Description
Timestamp	Submission time (if implemented or added later)
ReceptorFile	PDB filename for the receptor
LigandFile	PDB filename for the ligand
Email	Email used for the submission
JobName	Generated job name
Response	Server response text
Data Retention Policy:
Results are automatically deleted after 14 days.

Web Interface Features:

User Dashboard:
A simple HTML dashboard may display the status of each job, auto-refreshing every 10 seconds.
Example snippet:
html
Copy
<div class="status-board">
  <h2>Job job_id: <span class="status">QUEUED</span></h2>
  <div class="loader"></div>
  <p>Auto-refreshing in 10 seconds...</p>
</div>
Real-time status updates, browser notifications, and a mobile-responsive design are planned features.
New Submission & Error Analysis:
You can re-run the code to submit new jobs. If you encounter errors, use the bugfixes.py script to analyze which job IDs were problematic and adjust your input folders accordingly.

Execution Steps
Set Up Directories:
Create the following folders (if they do not already exist) under your project’s data folder:

receptor_pdbs (or submit_jobs_receptors if using the dedicated submission folders)
ligand_pdbs (or submit_jobs_ligands)
Place Input Files:
Ensure that the PDB files for receptors and ligands are placed in their respective directories.

Run the Script:
Execute your Node.js script:

bash
Copy
node path/to/your/script.js
Monitor the terminal for upload progress and check responses.csv (located in the data folder) for the submission responses.

References
Protein Data Bank (RCSB):
https://www.rcsb.org
AlphaFold DB:
https://alphafold.ebi.ac.uk
HDOCK Server:
http://hdock.phys.hust.edu.cn
Node.js Documentation:
https://nodejs.org/en/docs
Support Contact:
For issues with HDOCK submissions, please contact: hdock@hust.edu.cn
# Node.js Execution Guide for HDOCK Upload Script

This guide explains how to set up and execute the Node.js scripts for uploading receptor and ligand files via HDOCK.

## Prerequisites

- **Node.js:** Ensure you have Node.js (v12 or later) installed.  
  Check your version with:
  ```bash
  node -v


Script Architecture Overview
File Handling System
The script processes structural biology files from two designated directories:

Receptor Directory: Default path ../data/receptor_pdbs/ containing PDB-format files

Ligand Directory: Default path ../data/ligand_pdbs/ with ligand structure files

The system supports both traditional PDB files from the RCSB database and custom structural predictions from AlphaFold DB. Batch processing enables simultaneous handling of multiple receptor-ligand pairs.

Submission Workflow
Request Preparation Phase
For each receptor-ligand combination, the script:

Generates multipart/form-data POST requests

Implements email rotation strategy (alternates between 10 submissions)

Validates file integrity before submission

Job Execution Process
Core submission functionality uses HTTP POST:

javascript
Copy
const response = await fetch('http://hdock.phys.hust.edu.cn/submit', {
  method: 'POST',
  body: formData,
  headers: {
    'User-Agent': 'HDOCK Automation Client/1.0'
  }
});
The system includes error handling with:

Automatic retry mechanism for failed submissions

Network timeout protection (default: 30 seconds)

Concurrent request throttling

Results Tracking
All server responses log to responses.csv with:

Timestamp of submission

Receptor and ligand filenames

Email used for notification

Raw server response

Job status indicators

Web Interface Components
Job Status Dashboard
Real-time monitoring interface features:

html
Copy
<!-- Status display container -->
<div class="job-monitor">
  <h2>Job Status: <span id="jobStatus">QUEUED</span></h2>
  <div class="refresh-counter">
    Auto-refreshing in <span id="countdown">10</span> seconds
  </div>
</div>
Run HTML
Key functionality:

Automatic page refresh every 10 seconds

Browser notification integration

Mobile-responsive layout using CSS Grid

Persistent session storage for interrupted connections

Navigation System
User interface includes:

Bookmarkable job-specific URLs

Direct result sharing via generated links

Quick-access controls:

New submission button

Previous results archive

Documentation portal

Maintenance Protocols
Data Retention Policy
Successful job results: 14-day storage

Failed submissions: 48-hour error log retention

Automated cleanup scheduler

Error Recovery
For failed submissions:

Review errors.log for specific failure codes

Use bugfixes.py utility to analyze problematic Job IDs

Rebuild submission queue with missing pairs

Reference Documentation
Resource	Description	URL
RCSB PDB	Protein Data Bank repository	https://www.rcsb.org
AlphaFold DB	AI-predicted protein structures	https://alphafold.ebi.ac.uk
HDOCK Server	Docking service endpoint	http://hdock.phys.hust.edu.cn
Node.js Docs	Runtime documentation	https://nodejs.org/en/docs
Technical Support: hdock@hust.edu.cn | Response time: 24-48 business hours
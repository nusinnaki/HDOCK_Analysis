// script.js
/*
For this code to function you have to make sure you do not submit more jobs than allowed.
For example, if you have 100 jobs and 10 email addresses it will work. 
But if you have 100 jobs and 9 email addresses, it won't work since the website has a limit.

Before starting, create the following folders inside your "data" folder:
  - submit_jobs_receptors
  - submit_jobs_ligands

The input files (PDB files) should be placed in these folders, and they can change as needed.
*/

// ============================================================
// Configuration Variables (Edit these as needed)
// ============================================================
const path = require("path");
const fs = require("fs");
const axios = require("axios");
const FormData = require("form-data");

// Set the base directory to the "data" folder at the project root.
const baseDir = path.join(__dirname, "../data");

// Updated input directories: for receptors and ligands submissions.
const receptorDir = path.join(baseDir, "submit_jobs_receptors");
const ligandDir = path.join(baseDir, "submit_jobs_ligands");

// Output CSV file for responses is saved in the data folder.
const outputCsv = path.join(baseDir, "responses.csv");

// Upload URL for HDOCK
const uploadUrl = "http://hdock.phys.hust.edu.cn/runhdock.php";

// Email configuration: list of emails and rotation interval (rotate email every N calls)
const emails = [
  "nusinnaki@hotmail.com",
  "nusinnaki@gmail.com",
  "n.nua@hotmail.com",
  "nusin.naki@uni-konstanz.de",
  "nusinnaki@icloud.com",
  "sara.zumerle@iov.veneto.it",
  "giulia.zampardi@iov.veneto.it",
  "annavera.ventura@iov.veneto.it",
  "ventura.annav@gmail.com",
  "ada.tushe@iov.veneto.it",
  "elena.marinelli.1@studenti.unipd.it",
];
const emailRotationInterval = 10; // rotate email every 10 upload calls
// ============================================================

// Helper function to read files from a directory
function getFiles(dir) {
  return new Promise((resolve, reject) => {
    fs.readdir(dir, (err, files) => {
      if (err) reject(err);
      else resolve(files);
    });
  });
}

// Function to perform one upload call using async/await
async function uploadCall(receptorFile, ligandFile, email, jobName) {
  const form = new FormData();

  // Append form fields (pdbfile1: receptor, pdbfile2: ligand)
  form.append("pdbfile1", fs.createReadStream(path.join(receptorDir, receptorFile)));
  form.append("pdbid1", "");
  form.append("fastaseq1", "");
  form.append("fastafile1", "");

  form.append("pdbfile2", fs.createReadStream(path.join(ligandDir, ligandFile)));
  form.append("pdbid2", "");
  form.append("ligtyp", "");
  form.append("fastaseq2", "");
  form.append("fastafile2", "");

  // Optional fields
  form.append("symmetry", "");
  form.append("saxsfile", "");
  form.append("sitenum1", "");
  form.append("sitefile1", "");
  form.append("sitenum2", "");
  form.append("sitefile2", "");
  form.append("restrnum", "");
  form.append("restrfile", "");

  // Required email and job name
  form.append("email", email);
  form.append("jobname", jobName);
  form.append("upload", "Submit");

  // Set up headers similar to your curl command.
  const headers = {
    ...form.getHeaders(),
    Accept:
      "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,de;q=0.7",
    "Cache-Control": "max-age=0",
    Connection: "keep-alive",
    Origin: "http://hdock.phys.hust.edu.cn",
    Referer: "http://hdock.phys.hust.edu.cn/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
  };

  try {
    const response = await axios.post(uploadUrl, form, { headers });
    return response.data; // Return the website's response
  } catch (err) {
    return "Error: " + err.message;
  }
}

// Main async function: Reads files, iterates over each combination, rotates emails, and logs responses.
async function main() {
  try {
    // Get list of receptor files (only .pdb files)
    let receptorFiles = await getFiles(receptorDir);
    receptorFiles = receptorFiles.filter(file => file.endsWith(".pdb"));

    // Get list of ligand files (only .pdb files)
    let ligandFiles = await getFiles(ligandDir);
    ligandFiles = ligandFiles.filter(file => file.endsWith(".pdb"));

    // Create (or overwrite) the CSV file and write the header row.
    fs.writeFileSync(outputCsv, "receptor_file,ligand_file,email,job_name,response\n");

    let callCount = 0;
    let emailIndex = 0;

    // For every receptor file, iterate over each ligand file.
    for (const receptorFile of receptorFiles) {
      for (const ligandFile of ligandFiles) {
        // Rotate email every emailRotationInterval calls.
        if (callCount > 0 && callCount % emailRotationInterval === 0) {
          emailIndex = (emailIndex + 1) % emails.length;
        }
        const currentEmail = emails[emailIndex];
        // Generate a job name; customize as needed.
        const jobName = `${path.parse(receptorFile).name}_${path.parse(ligandFile).name}`;

        console.log(
          `Uploading: Receptor: ${receptorFile}, Ligand: ${ligandFile}, Email: ${currentEmail}, Job: ${jobName}`
        );
        const response = await uploadCall(receptorFile, ligandFile, currentEmail, jobName);

        // Prepare a CSV row, escaping any quotes in the response.
        const csvRow = `"${receptorFile}","${ligandFile}","${currentEmail}","${jobName}","${String(response).replace(/"/g, '""')}"\n`;
        fs.appendFileSync(outputCsv, csvRow);

        callCount++;
      }
    }
    console.log("All uploads completed. Please check the responses.csv file for details.");
  } catch (err) {
    console.error("An error occurred:", err);
  }
}

// Start the script
main();

// script.js

// Required modules
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");

// Folder paths (make sure these folders exist in the same directory as the script)
const receptorDir = path.join(__dirname, "receptor_pdbs");
const ligandDir = path.join(__dirname, "ligand_pdbs");
const outputCsv = path.join(__dirname, "responses.csv");

// List of 10 email addresses (modify with your actual emails)
const emails = [
  "umutnaki.f@gmail.com",
  "zelalnaki@me.com",
  "gulcindogan96@hotmail.com",
  "nusinnaki@icloud.com",
  "sara.zumerle@iov.veneto.it",
  "giulia.zampardi@iov.veneto.it",
  "annavera.ventura@iov.veneto.it",
  "ventura.annav@gmail.com",
  "ada.tushe@iov.veneto.it",
  "elena.marinelli.1@studenti.unipd.it",
];

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
  const url = "http://hdock.phys.hust.edu.cn/runhdock.php";
  const form = new FormData();

  // Append form fields (replicating your curl command)
  // Note: pdbfile1 is assumed to be the receptor file and pdbfile2 is the ligand file.
  form.append(
    "pdbfile1",
    fs.createReadStream(path.join(receptorDir, receptorFile))
  );
  form.append("pdbid1", "");
  form.append("fastaseq1", "");
  // If you have a fastafile1 file to send, update the code accordingly.
  form.append("fastafile1", "");

  form.append(
    "pdbfile2",
    fs.createReadStream(path.join(ligandDir, ligandFile))
  );
  form.append("pdbid2", "");
  form.append("ligtyp", "");
  form.append("fastaseq2", "");
  form.append("fastafile2", "");

  // The remaining optional fields are appended as empty strings.
  form.append("symmetry", "");
  form.append("saxsfile", "");
  form.append("sitenum1", "");
  form.append("sitefile1", "");
  form.append("sitenum2", "");
  form.append("sitefile2", "");
  form.append("restrnum", "");
  form.append("restrfile", "");

  // Email and job name are required.
  form.append("email", email);
  form.append("jobname", jobName);
  form.append("upload", "Submit");

  // Set up headers similar to the curl command.
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
    const response = await axios.post(url, form, { headers });
    return response.data; // returns the response from the website
  } catch (err) {
    return "Error: " + err.message;
  }
}

// Main async function that reads the folders, iterates over files, and rotates emails.
async function main() {
  try {
    // Get lists of files from each folder. 2 files only
    let receptorFiles = await getFiles(receptorDir);
    receptorFiles = receptorFiles.filter((file, index) => file.includes(".pdb"));
    // 40 files/day
    let ligandFiles = await getFiles(ligandDir);
    ligandFiles = ligandFiles.filter((file, index) => file.includes(".pdb"));

    // Create (or overwrite) the CSV file and write the header row.
    fs.writeFileSync(
      outputCsv,
      "ReceptorFile,LigandFile,Email,JobName,Response\n"
    );

    let callCount = 0;
    let emailIndex = 0;

    // For every receptor file, try all ligand files.
    for (const receptorFile of receptorFiles) {
      for (const ligandFile of ligandFiles) {
        // Rotate email every 10 calls
        if (callCount > 0 && callCount % 10 === 0) {
          emailIndex = (emailIndex + 1) % emails.length;
        }
        const currentEmail = emails[emailIndex];
        // Generate a job name; you can customize this naming scheme.
        const jobName = `${path.parse(receptorFile).name}_${path.parse(ligandFile).name
          }`;

        console.log(
          `Uploading: Receptor: ${receptorFile}, Ligand: ${ligandFile}, Email: ${currentEmail}, Job: ${jobName}`
        );
        const response = await uploadCall(
          receptorFile,
          ligandFile,
          currentEmail,
          jobName
        );

        // Prepare a CSV row. Double quotes are used to escape any commas in the fields.
        const csvRow = `"${receptorFile}","${ligandFile}","${currentEmail}","${jobName}","${String(
          response
        ).replace(/"/g, '""')}"\n`;
        fs.appendFileSync(outputCsv, csvRow);

        callCount++;
      }
    }
    console.log(
      "All uploads completed. Please check the responses.csv file for details."
    );
  } catch (err) {
    console.error("An error occurred:", err);
  }
}

// Start the script
main();

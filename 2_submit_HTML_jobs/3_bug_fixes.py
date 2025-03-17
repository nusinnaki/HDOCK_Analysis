import os
import pandas as pd
import shutil

# -------------- Configuration --------------
# Path to your final responses CSV file (using project folder structure)
csv_file = os.path.join(os.getcwd(), "data", "hdock_responses", "final_responses.csv")

# Source directories (these should never change after being created)
source_receptor_dir = os.path.join(os.getcwd(), "data", "receptor_pdbs")
source_ligand_dir = os.path.join(os.getcwd(), "data", "ligand_pdbs")

# Submission directories (these will be re-created based on failed jobs)
submit_receptor_dir = os.path.join(os.getcwd(), "data", "submit_jobs_receptors")
submit_ligand_dir = os.path.join(os.getcwd(), "data", "submit_jobs_ligands")

# -------------------------------------------

# Load final CSV file
df = pd.read_csv(csv_file)

# Determine failed jobs by grouping on 'job_name'
failed_jobs = (
    df.groupby('job_name')
      .apply(lambda g: (g['download_ID'] == 'failed').all())
      .loc[lambda x: x].index.tolist()
)

if not failed_jobs:
    print("No completely failed jobs found in the CSV.")
else:
    print("\nPlanned jobs for re-submission (failed combinations):")
    # Filter the dataframe to only include failed jobs (using job_name)
    failed_df = df[df['job_name'].isin(failed_jobs)]
    # Get unique receptor and ligand file combinations
    planned_jobs = failed_df[['receptor_file', 'ligand_file', 'job_name']].drop_duplicates()
    print(planned_jobs.to_string(index=False))

# Also, get unique individual receptor and ligand files that were part of failed jobs.
receptor_files = failed_df['receptor_file'].unique().tolist()
ligand_files = failed_df['ligand_file'].unique().tolist()

print("\nUnique receptor files from failed jobs:")
print(receptor_files)
print("\nUnique ligand files from failed jobs:")
print(ligand_files)

# --------------
# Recreate submission folders:
# Delete submission folders if they exist, then re-create them.
for folder in [submit_receptor_dir, submit_ligand_dir]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# Copy the failed receptor files from the source directory to the submission directory.
print("\nCopying receptor files for re-submission...")
for fname in receptor_files:
    source_file = os.path.join(source_receptor_dir, fname)
    if os.path.exists(source_file):
        shutil.copy(source_file, submit_receptor_dir)
        print(f"Copied: {fname}")
    else:
        print(f"Source receptor file not found: {fname}")

# Copy the failed ligand files from the source directory to the submission directory.
print("\nCopying ligand files for re-submission...")
for fname in ligand_files:
    source_file = os.path.join(source_ligand_dir, fname)
    if os.path.exists(source_file):
        shutil.copy(source_file, submit_ligand_dir)
        print(f"Copied: {fname}")
    else:
        print(f"Source ligand file not found: {fname}")

# Inform the user of the next step.
print("\n✅ Submission folders have been recreated with files from failed jobs.")
print("👉 Now go back to submit_jobs.js and re-submit the failed jobs.")
# Note: When the folders are recreated I will basically go back to submit_jobs.js and re-submit the failed jobs.

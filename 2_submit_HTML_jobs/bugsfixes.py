import pandas as pd
import os

# Path to your CSV file
csv_file = '/Users/nusin/Desktop/hdock_responses/final_responses.csv'

# Path to directories
receptor_dir = '/Users/nusin/Desktop/jobs_sd/receptor_pdbs'
ligand_dir = '/Users/nusin/Desktop/jobs_sd/ligand_pdbs'

# Load data and find completely failed jobs
df = pd.read_csv(csv_file)

# Get jobs where ALL attempts failed (no successful rows)
failed_jobs = (
    df.groupby('JobName')
    .apply(lambda g: (g['download_ID'] == 'failed').all())
    .loc[lambda x: x]
    .index.tolist()
)

# Get unique receptor/ligand pairs from failed jobs
failed_pairs = df[df['JobName'].isin(failed_jobs)][['ReceptorFile', 'LigandFile']].drop_duplicates()

# Get unique individual files
receptor_files = df[df['JobName'].isin(failed_jobs)]['ReceptorFile'].unique().tolist()
ligand_files = df[df['JobName'].isin(failed_jobs)]['LigandFile'].unique().tolist()

def real_cleanup(directory, keep_list, file_type):
    """Actually removes files not needed for resubmission"""
    print(f"\n{file_type.upper()} CLEANUP: {directory}")
    deleted_count = 0
    kept_count = 0
    
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath):
            if fname not in keep_list:
                os.remove(fpath)
                print(f"Deleted: {fname}")
                deleted_count += 1
            else:
                kept_count += 1
                
    print(f"\n{file_type} cleanup summary:")
    print(f"Files kept: {kept_count}")
    print(f"Files deleted: {deleted_count}")

# Execute cleanup immediately
print("\n=== STARTING AUTOMATED CLEANUP ===")
real_cleanup(receptor_dir, receptor_files, "receptor")
real_cleanup(ligand_dir, ligand_files, "ligand")
print("\nCleanup completed without confirmation!")
import os
import requests
import pandas as pd

# ============================================================
# Configuration Variables (Edit these as needed)
# ============================================================
# Use the 'data' folder as the base directory
BASE_DIR = os.path.join(os.getcwd(), "data")
RCSB_PDB_DIR = os.path.join(BASE_DIR, 'receptor_pdbs')
ALPHAFOLD_PDB_DIR = os.path.join(BASE_DIR, 'receptor_pdbs')  # You can change this if you want a separate folder
INPUT_CSV_FILE = os.path.join(BASE_DIR, "df_receptor_HO-1.csv")
RCSB_DOWNLOAD_BASE_URL = "https://files.rcsb.org/download/"
ALPHAFOLD_DOWNLOAD_BASE_URL = "https://alphafold.ebi.ac.uk/files/"
# ============================================================

os.makedirs(RCSB_PDB_DIR, exist_ok=True)
os.makedirs(ALPHAFOLD_PDB_DIR, exist_ok=True)

def download_rcsb_pdb(identifier, output_directory):
    pdb_url = f"{RCSB_DOWNLOAD_BASE_URL}{identifier}.pdb"
    try:
        response = requests.get(pdb_url, timeout=10)
        response.raise_for_status()
        pdb_file_path = os.path.join(output_directory, f"{identifier}.pdb")
        with open(pdb_file_path, 'wb') as pdb_file:
            pdb_file.write(response.content)
        print(f"Downloaded (RCSB): {identifier}.pdb")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {identifier} from RCSB: {e}")

df_receptor_hmox1 = pd.read_csv(INPUT_CSV_FILE)
pdb_ids = df_receptor_hmox1.loc[~df_receptor_hmox1['identifier'].str.startswith("AF-"), 'identifier'].tolist()

for pdb_id in pdb_ids:
    download_rcsb_pdb(pdb_id, RCSB_PDB_DIR)

def download_alphafold_pdb(identifier, output_directory):
    pdb_url = f"{ALPHAFOLD_DOWNLOAD_BASE_URL}{identifier}-model_v4.pdb"
    try:
        response = requests.get(pdb_url, timeout=10)
        response.raise_for_status()
        pdb_file_path = os.path.join(output_directory, f"{identifier}.pdb")
        with open(pdb_file_path, 'wb') as pdb_file:
            pdb_file.write(response.content)
        print(f"Downloaded (AlphaFold): {identifier}.pdb")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {identifier} from AlphaFold: {e}")

for _, row in df_receptor_hmox1.iterrows():
    identifier = row['identifier']
    if identifier.startswith("AF-"):
        download_alphafold_pdb(identifier, ALPHAFOLD_PDB_DIR)

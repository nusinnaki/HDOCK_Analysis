import pandas as pd
import os
import requests
from typing import Tuple

# ============================================================
# Configuration Variables (Edit these as needed)
# ============================================================
BASE_DIR = "/Users/nusin/Library/Mobile Documents/com~apple~CloudDocs/Desktop/IOV/3_Projects/PPI/1_Input_Proteins_pdbs"
ALL_LIGANDS_CSV = os.path.join(BASE_DIR, "df_all_ligands.csv")
FILTERED_LIGANDS_CSV = os.path.join(BASE_DIR, "df_filtered_ligands.csv")
DOWNLOADED_LIGANDS_CSV = os.path.join(BASE_DIR, "df_downloaded_ligands.csv")
LIGAND_PDB_DIR = os.path.join(BASE_DIR, "ligand_pdbs")
# ============================================================

# -----------------------------
# Filtering Section (unchanged)
# -----------------------------

def parse_position_length(position: str) -> int:
    """Calculate length from Positions string (e.g., '1-98')."""
    if pd.isna(position) or position == 'N/A':
        return 0
    try:
        start, end = map(int, position.split('-'))
        return end - start + 1
    except (ValueError, AttributeError):
        return 0

def filter_ligand_structures(ligand_df: pd.DataFrame) -> pd.DataFrame:
    """Filter ligand structures with logic matching the data sample."""
    filtered_results = []
    
    for accession, group in ligand_df.groupby("accession"):
        predicted = group[group['method'].str.contains('predicted', case=False, na=False)]
        others = group[~group.index.isin(predicted.index)]
        
        selected = predicted.copy()
        
        if len(selected) < 3:
            others = others.copy()
            others["position_length"] = others["positions"].apply(parse_position_length)
            
            others = others.sort_values(
                by=["position_length", "resolution"],
                ascending=[False, True]
            )
            
            remaining = 3 - len(selected)
            selected = pd.concat([selected, others.head(remaining)])
        
        filtered_results.append(selected.head(3))
    
    return pd.concat(filtered_results).reset_index(drop=True).fillna('N/A')

def apply_filters_and_save():
    input_path = ALL_LIGANDS_CSV
    output_path = FILTERED_LIGANDS_CSV
    
    df = pd.read_csv(input_path)
    filtered_df = filter_ligand_structures(df)
    filtered_df.to_csv(output_path, index=False)
    print(f"✅ Saved filtered data ({len(filtered_df)} rows) to {output_path}")

# -----------------------------
# Download Section (modified)
# -----------------------------

def download_pdb(identifier: str, output_dir: str) -> Tuple[bool, str]:
    """Download PDB file with existence check."""
    file_path = os.path.join(output_dir, f"{identifier}.pdb")
    
    # Check if file already exists
    if os.path.exists(file_path):
        return True, f"Already exists: {identifier}.pdb"
    
    if identifier.startswith("AF-"):
        url = f"https://alphafold.ebi.ac.uk/files/{identifier}-model_v4.pdb"
    else:
        url = f"https://files.rcsb.org/download/{identifier}.pdb"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return True, f"Downloaded: {identifier}"
    except Exception as e:
        return False, f"Failed {identifier}: {str(e)}"

def verify_downloads(df: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """Verify which files actually exist in the download directory."""
    df['downloaded'] = df['identifier'].apply(
        lambda x: 'yes' if (not pd.isna(x)) and 
        os.path.exists(os.path.join(output_dir, f"{x}.pdb")) 
        else 'no'
    )
    return df

def download_and_update():
    filtered_path = FILTERED_LIGANDS_CSV
    output_dir = LIGAND_PDB_DIR
    final_output_path = DOWNLOADED_LIGANDS_CSV
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(filtered_path)
    failed = []
    
    for identifier in df['identifier'].dropna().unique():
        success, message = download_pdb(identifier, output_dir)
        print(message)
        if not success:
            failed.append(identifier)
    
    df = verify_downloads(df, output_dir)
    df.to_csv(final_output_path, index=False)
    print(f"\n✅ Final data saved to {final_output_path}")
    
    if failed:
        print("\n❌ Failed downloads:")
        print("\n".join(failed))
    else:
        print("\n🎉 All files downloaded successfully!")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    apply_filters_and_save()
    download_and_update()

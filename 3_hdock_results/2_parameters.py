import os
import glob
import pandas as pd
import numpy as np

# ============================================================
# Configuration Variables
# ============================================================
data_dir = '/Users/nusin/Desktop/Hdock_results'
ligand_folder = os.path.join(data_dir, 'hdock_output')
mapped_csv_path = os.path.join(data_dir, 'mapped_ligands.csv')  # Updated file name
output_csv_path = os.path.join(data_dir, 'hdock_out_parameters.csv')
# ============================================================

def process_out_files(ligand_folder):
    """
    Process .out files to extract metrics for all parameters.
    For each .out file (filename starting with 'hdock_' and ending with '.out'),
    it extracts the download_ID from the file name and reads the file.
    It calculates the following metrics for each parameter:
        - first value
        - average of first 10 values
        - average of first 100 values
        - average of first 1000 values
        - average of all values
    Returns a DataFrame with one row per download_ID.
    """
    # Recursively find all .out files in the given folder
    all_out_files = sorted(glob.glob(os.path.join(ligand_folder, '**/*.out'), recursive=True))
    
    # Define columns expected in the .out files
    cols = [
        "Translation_X", "Translation_Y", "Translation_Z", 
        "Rotation_X", "Rotation_Y", "Rotation_Z", 
        "Binding_Score", "RMSD", "Translational_ID"
    ]
    
    results = []
    
    for out_file in all_out_files:
        basename = os.path.basename(out_file)
        # Only process files that follow the expected naming convention
        if not (basename.startswith('hdock_') and basename.endswith('.out')):
            print(f"Skipping unexpected file: {basename}")
            continue
        
        download_ID = basename[len('hdock_'):-len('.out')]
        print(f"Processing download ID: {download_ID}")
        
        try:
            # Read the .out file using whitespace as the delimiter.
            df_out = pd.read_csv(
                out_file, 
                sep='\s+', 
                header=None, 
                names=cols, 
                engine='python', 
                on_bad_lines='skip'
            )
            
            result = {'download_ID': download_ID}
            
            # For each parameter, compute the desired metrics.
            for param in cols:
                series = pd.to_numeric(df_out[param], errors='coerce').dropna()
                result[f'first_{param}'] = series.iloc[0] if len(series) > 0 else np.nan
                result[f'avg10_{param}'] = series.iloc[:10].mean() if len(series) > 0 else np.nan
                result[f'avg100_{param}'] = series.iloc[:100].mean() if len(series) > 0 else np.nan
                result[f'avg1000_{param}'] = series.iloc[:1000].mean() if len(series) > 0 else np.nan
                result[f'avgAll_{param}'] = series.mean() if len(series) > 0 else np.nan
                
            results.append(result)
        except Exception as e:
            print(f"Error processing {out_file}: {e}")
            continue
    
    return pd.DataFrame(results)

# Process all .out files to get the computed metrics DataFrame.
metrics_df = process_out_files(ligand_folder)

# Read the original mapped CSV file.
mapped_df = pd.read_csv(mapped_csv_path)

# Merge the computed metrics with the mapped CSV data on the download_ID column.
# Using a left join to preserve all columns from mapped_df.
merged_df = pd.merge(mapped_df, metrics_df, on="download_ID", how="left")

# Reorder columns: first all columns from mapped_df, then any additional columns (metrics)
mapped_columns = mapped_df.columns.tolist()
additional_columns = [col for col in merged_df.columns if col not in mapped_columns]
merged_df = merged_df[mapped_columns + additional_columns]

# Write the merged DataFrame to a new CSV file.
merged_df.to_csv(output_csv_path, index=False)

print("hdock_out_parameters.csv has been created.")

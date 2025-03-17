import os
import pandas as pd

# ============================================================
# Configuration Variables
# ============================================================
data_dir = '/Users/nusin/Desktop/Hdock_results'
final_responses_path = os.path.join(data_dir, 'final_responses.csv')
df_all_ligands_path = os.path.join(data_dir, 'df_all_ligands.csv')
output_path = os.path.join(data_dir, 'mapped_ligands.csv')  # Output file name changed
# ============================================================

# Read the input files
final_responses = pd.read_csv(final_responses_path)
df_all_ligands = pd.read_csv(df_all_ligands_path)

# Step 1: Remove rows where "valid_download" is "failed"
final_responses = final_responses[final_responses['valid_download'] != 'failed']

# Step 2: Extract identifier from LigandFile (remove the .pdb extension)
final_responses['identifier'] = final_responses['LigandFile'].str.replace('.pdb', '', regex=False)

# Step 3: Merge final_responses with df_all_ligands using the identifier column
merged = pd.merge(final_responses, df_all_ligands, on='identifier', how='left')

# Step 4: Reorder columns so that final_responses columns come first, followed by df_all_ligands columns
# List of final_responses columns (as provided)
final_response_cols = ['download_ID', 'ReceptorFile', 'LigandFile', 'Email', 'JobName', 'view_links', 'download_links', 'expected_count', 'zero_out', 'valid_download']

# Get the additional columns from df_all_ligands (including 'identifier' if present)
additional_cols = [col for col in merged.columns if col not in final_response_cols]

# Create the new column order and reorder the DataFrame
new_cols = final_response_cols + additional_cols
merged = merged[new_cols]

# Step 5: Save the merged DataFrame to a new CSV file named mapped_ligands.csv
merged.to_csv(output_path, index=False)

print(f"Successfully created {output_path}")
print(merged.head())

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# Configuration Variables
# ============================================================
data_dir = '/Users/nusin/Desktop/Hdock_results'
base_folder = os.path.join(data_dir, 'hdock_output')  # Folder containing all hdock .out files
hdock_out_parameters_csv_path = os.path.join(data_dir, 'hdock_out_parameters.csv')  # Input CSV with protein information
plot_folder = os.path.join(data_dir, 'protein_plots')   # Output folder for protein plots
# ============================================================

# Define columns expected in the .out files
cols = [
    "Translation_X", "Translation_Y", "Translation_Z", 
    "Rotation_X", "Rotation_Y", "Rotation_Z", 
    "Binding_Score", "RMSD", "Translational_ID"
]

# Read the input CSV file for protein information
mapped_df = pd.read_csv(hdock_out_parameters_csv_path)

# Create an output directory for protein plots if it doesn't exist
os.makedirs(plot_folder, exist_ok=True)

# Group the CSV by gene_symbol so that all rows with the same gene are in one graph
for gene, group_df in mapped_df.groupby("gene_symbol"):
    # Get protein_name and short_name from the first row of the group (if available)
    first_row = group_df.iloc[0]
    protein_name = first_row.get('protein_name', 'Unknown')
    short_name = first_row.get('short_name', '')
    if pd.isna(short_name) or short_name == '':
        protein_title = protein_name
    else:
        protein_title = f"{protein_name}, ({short_name})"
    
    # Create a figure with 9 subplots (3 rows x 3 columns)
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    # Set suptitle as requested:
    fig.suptitle(f"First 50 entries for protein: {protein_title}\nGene involved: {gene}", fontsize=16)
    
    # Initialize a dictionary to track plotted JobNames for each parameter (one per subplot)
    plotted_labels = {i: set() for i in range(len(cols))}
    
    # Process each row in the group (each corresponds to one JobName)
    for idx, row in group_df.iterrows():
        download_ID = row['download_ID']
        jobName = row['JobName']
        
        # Search for the corresponding .out file using a recursive glob pattern.
        out_pattern = os.path.join(base_folder, '**', f'hdock_{download_ID}.out')
        out_files = glob.glob(out_pattern, recursive=True)
        
        if not out_files:
            print(f"No .out file found for download_ID: {download_ID}")
            continue
        
        out_file = out_files[0]  # Use the first matching file
        print(f"Processing gene: {gene}, JobName: {jobName}, download_ID: {download_ID} from file: {out_file}")
        
        try:
            # Read the .out file. Lines starting with '#' are treated as comments.
            df_out = pd.read_csv(
                out_file, 
                sep='\s+', 
                header=None, 
                names=cols, 
                engine='python', 
                on_bad_lines='skip',
                comment='#'
            )
        except Exception as e:
            print(f"Error reading {out_file}: {e}")
            continue
        
        # Extract the first 50 entries (or as many as available)
        df_first50 = df_out.head(50)
        
        # Loop over each parameter and plot its values on the corresponding subplot
        for i, param in enumerate(cols):
            ax = axes[i // 3, i % 3]
            # Convert values to numeric (non-numeric become NaN) and plot
            values = pd.to_numeric(df_first50[param], errors='coerce')
            # Only add label if this JobName hasn't been plotted yet in this subplot
            if jobName not in plotted_labels[i]:
                ax.plot(df_first50.index, values, marker='o', linestyle='-', label=jobName)
                plotted_labels[i].add(jobName)
            else:
                ax.plot(df_first50.index, values, marker='o', linestyle='-')
            ax.set_title(param)
            ax.set_xlabel("Entry")
            ax.set_ylabel(param)
    
    # Add legends to each subplot so the lines are labeled with JobName
    for i in range(3):
        for j in range(3):
            axes[i, j].legend()
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to include the suptitle
    
    # Save the figure with the gene_symbol in the filename
    plot_filename = os.path.join(plot_folder, f"{gene}_first50.png")
    plt.savefig(plot_filename)
    plt.close()
    print(f"Saved plot for gene {gene} to {plot_filename}")

print("All grouped protein plots have been generated and saved in the 'protein_plots' folder.")

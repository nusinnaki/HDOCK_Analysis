import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# Configuration Variables
# ============================================================
data_dir = '/Users/nusin/Desktop/Hdock_results'
input_csv_path = os.path.join(data_dir, 'hdock_out_parameters.csv')
output_folder = os.path.join(data_dir, 'parameter_plots')
os.makedirs(output_folder, exist_ok=True)
# ============================================================

# Define the parameters we want to plot
params = [
    "Translation_X", "Translation_Y", "Translation_Z", 
    "Rotation_X", "Rotation_Y", "Rotation_Z", 
    "Binding_Score", "RMSD", "Translational_ID"
]

# Define the metric types to plot
metrics = ["first", "avg10", "avg100", "avg1000"]

# Load the CSV file that includes computed metrics.
df = pd.read_csv(input_csv_path)

# Loop over each metric type and parameter
for metric in metrics:
    for param in params:
        col_name = f"{metric}_{param}"
        if col_name not in df.columns:
            print(f"Column {col_name} not found in the DataFrame. Skipping...")
            continue

        # Sort proteins by the metric column (ascending: lower scores are better)
        df_sorted = df.sort_values(by=col_name, ascending=True)
        df_top50 = df_sorted.head(50)

        # Use only short_name as label if exists; otherwise, use protein_name; otherwise, use download_ID
        if "short_name" in df_top50.columns:
            labels = df_top50["short_name"].astype(str)
        elif "protein_name" in df_top50.columns:
            labels = df_top50["protein_name"].astype(str)
        else:
            labels = df_top50["download_ID"].astype(str)

        values = df_top50[col_name]

        # Create a horizontal bar plot
        plt.figure(figsize=(10, 8))
        plt.barh(labels, values, color='skyblue')
        plt.xlabel(col_name)
        plt.title(f"Top 50 Proteins by {col_name}")
        plt.gca().invert_yaxis()  # Invert y-axis so the best (lowest) scores are at the top
        plt.tight_layout()

        # Save the plot
        output_file = os.path.join(output_folder, f"{col_name}_top50.png")
        plt.savefig(output_file)
        plt.close()

        print(f"Saved plot for {col_name} to {output_file}")

print(f"All parameter plots have been generated and saved in '{output_folder}'.")

import glob
import os
import tarfile
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Global base URL for HDOCK
BASE_URL = "http://hdock.phys.hust.edu.cn/data/"

def extract_job_id(html):
    """Extract job ID from HTML response."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            text = title_tag.get_text(strip=True)
            if "HDOCK Server: Job results for" in text:
                return text.split("for")[-1].strip().split()[0]
        return "failed"
    except Exception:
        return "failed"

def process_csv_files(directory):
    """Process response CSVs and add download metadata."""
    print("🔍 Processing CSV files...")
    csv_files = glob.glob(os.path.join(directory, "responses*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {directory}")
        return pd.DataFrame()

    dfs = []
    for file in csv_files:
        print(f"📂 Processing {os.path.basename(file)}...")
        df = pd.read_csv(file)
        df["download_ID"] = df["Response"].apply(
            lambda x: extract_job_id(x) if isinstance(x, str) else "failed"
        )
        df["view_links"] = df["download_ID"].apply(
            lambda x: f"{BASE_URL}{x}/" if x != "failed" else "failed"
        )
        df["download_links"] = df["download_ID"].apply(
            lambda x: f"{BASE_URL}{x}/all_results.tar.gz" if x != "failed" else "failed"
        )
        dfs.append(df)
    
    print(f"✅ Processed {len(dfs)} CSV files")
    return pd.concat(dfs, ignore_index=True)

def download_tar_gz_files(df, output_directory):
    """Download tar.gz files with validation checks."""
    print("\n⬇️ Starting downloads...")
    os.makedirs(output_directory, exist_ok=True)
    
    for idx, row in df.iterrows():
        url = row["download_links"]
        job_id = row["download_ID"]
        
        if url == "failed" or job_id == "failed":
            continue
            
        tar_path = os.path.join(output_directory, f"{job_id}.tar.gz")
        folder_path = os.path.join(output_directory, job_id)
        
        if os.path.exists(folder_path):
            print(f"⏩ Skipping {job_id} - already exists")
            continue
            
        try:
            if not os.path.exists(tar_path):
                print(f"🔽 Downloading {job_id}...")
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(tar_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"✅ Successfully downloaded {job_id}")
                else:
                    df.at[idx, "download_links"] = "failed"
                    print(f"❌ Failed to download {job_id} (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ Download failed for {job_id}: {str(e)}")
            df.at[idx, "download_links"] = "failed"

def extract_tar_gz_files(output_directory):
    """Extract downloaded archives."""
    print("\n📦 Extracting files...")
    for tar_file in glob.glob(os.path.join(output_directory, "*.tar.gz")):
        try:
            print(f"📂 Extracting {os.path.basename(tar_file)}...")
            with tarfile.open(tar_file, "r:gz") as tar:
                tar.extractall(path=output_directory)
            os.remove(tar_file)
            print(f"✅ Successfully extracted {os.path.basename(tar_file)}")
        except Exception as e:
            print(f"❌ Extraction failed for {os.path.basename(tar_file)}: {str(e)}")

def check_expected_count(df, output_directory, expected=113):
    """Check if folder contains expected number of files."""
    print("\n🔢 Validating file counts...")
    df["expected_count"] = df["download_ID"].apply(
        lambda x: "worked" if (
            x != "failed" and 
            os.path.exists(os.path.join(output_directory, x)) and 
            len(os.listdir(os.path.join(output_directory, x))) >= expected
        ) else "failed"
    )

def check_zero_binding_scores(df, output_directory):
    """Check if first binding score is zero."""
    print("\n🔍 Checking binding scores...")
    cols = [
        "Translation_X", "Translation_Y", "Translation_Z",
        "Rotation_X", "Rotation_Y", "Rotation_Z",
        "Binding_Score", "RMSD", "Translational_ID"
    ]
    
    def _check_score(job_id):
        if job_id == "failed":
            return "failed"
            
        try:
            out_file = glob.glob(os.path.join(output_directory, job_id, "*.out"))[0]
            df_out = pd.read_csv(out_file, sep='\s+', header=None, names=cols, 
                               engine='python', on_bad_lines='skip')
            first_score = pd.to_numeric(df_out["Binding_Score"].iloc[0], errors='coerce')
            return "failed" if first_score == 0 else "worked"
        except Exception as e:
            print(f"❌ Error processing {job_id}: {str(e)}")
            return "failed"
    
    df["zero_out"] = df["download_ID"].apply(_check_score)

def validate_final_status(df):
    """Calculate final validation status."""
    print("\n✅ Final validation...")
    status_columns = ["download_ID", "view_links", "download_links", "expected_count", "zero_out"]
    df["valid_download"] = df.apply(
        lambda row: "worked" if all(row[col] != "failed" for col in status_columns) else "failed",
        axis=1
    )

if __name__ == "__main__":
    # Configuration
    CSV_DIR = "/Users/nusin/Desktop/Hdock_responses"
    OUTPUT_DIR = os.path.join(CSV_DIR, "hdock_output")
    FINAL_CSV = os.path.join(CSV_DIR, "final_responses.csv")

    # Process data
    combined_df = process_csv_files(CSV_DIR)
    
    # Download and extract files
    download_tar_gz_files(combined_df, OUTPUT_DIR)
    extract_tar_gz_files(OUTPUT_DIR)
    
    # Add validation columns
    check_expected_count(combined_df, OUTPUT_DIR)
    check_zero_binding_scores(combined_df, OUTPUT_DIR)
    validate_final_status(combined_df)

    # Format final output
    final_columns = [
        'download_ID', 'ReceptorFile', 'LigandFile', 'Email', 'JobName',
        'view_links', 'download_links', 'expected_count', 'zero_out', 'valid_download'
    ]
    
    # Create final dataframe with only requested columns
    final_df = combined_df[final_columns]

    # Save results
    final_df.to_csv(FINAL_CSV, index=False)
    print(f"\n🎉 Final results saved to: {FINAL_CSV}")

    # Print summary
    print("\n📊 Validation Summary:")
    print("=" * 50)
    print(final_df[['valid_download', 'download_ID']].groupby('valid_download').count())
    print("\n🔧 Status Breakdown:")
    print("=" * 50)
    for column in ['expected_count', 'zero_out', 'valid_download']:
        print(f"\n{column.upper()} STATUS:")
        print(final_df[column].value_counts().to_string())
    
    print("\n✅ Processing complete!")
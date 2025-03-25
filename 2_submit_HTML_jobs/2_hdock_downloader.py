import glob
import os
import tarfile
import requests
import pandas as pd
from bs4 import BeautifulSoup

# ============================================================
# Configuration Variables
# ============================================================
BASE_DIR = os.path.join(os.getcwd(), "data")  # Store everything inside 'data' folder
RESPONSES_DIR = os.path.join(BASE_DIR, "hdock_responses")  # Folder for response CSVs
OUTPUT_DIR = os.path.join(BASE_DIR, "hdock_output")  # Folder for extracted outputs
FINAL_CSV = os.path.join(BASE_DIR, "final_responses.csv")  # Final deduplicated CSV

# Ensure directories exist
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# HDOCK Server Base URL
BASE_URL = "http://hdock.phys.hust.edu.cn/data/"
EXPECTED_FILES_COUNT = 113
# ============================================================

def extract_job_id(html):
    """Extract job ID from HDOCK HTML response."""
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

def process_csv_files():
    """Process HDOCK response CSVs and add metadata."""
    print("🔍 Processing CSV files...")
    csv_files = glob.glob(os.path.join(RESPONSES_DIR, "hdock_responses_*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {RESPONSES_DIR}")
        return pd.DataFrame()

    dfs = []
    for file in csv_files:
        print(f"📂 Processing {os.path.basename(file)}...")
        df = pd.read_csv(file)
        df["download_ID"] = df["Response"].apply(lambda x: extract_job_id(x) if isinstance(x, str) else "failed")
        df["view_links"] = df["download_ID"].apply(lambda x: f"{BASE_URL}{x}/" if x != "failed" else "failed")
        df["download_links"] = df["download_ID"].apply(lambda x: f"{BASE_URL}{x}/all_results.tar.gz" if x != "failed" else "failed")
        dfs.append(df)

    print(f"✅ Processed {len(dfs)} CSV files")
    return pd.concat(dfs, ignore_index=True)

def download_tar_gz_files(df):
    """Download tar.gz files with validation checks."""
    print("\n⬇️ Starting downloads...")
    
    for idx, row in df.iterrows():
        url = row["download_links"]
        job_id = row["download_ID"]
        
        if url == "failed" or job_id == "failed":
            continue
            
        tar_path = os.path.join(OUTPUT_DIR, f"{job_id}.tar.gz")
        folder_path = os.path.join(OUTPUT_DIR, job_id)
        
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

def extract_tar_gz_files():
    """Extract downloaded tar.gz files."""
    print("\n📦 Extracting files...")
    for tar_file in glob.glob(os.path.join(OUTPUT_DIR, "*.tar.gz")):
        try:
            print(f"📂 Extracting {os.path.basename(tar_file)}...")
            with tarfile.open(tar_file, "r:gz") as tar:
                tar.extractall(path=OUTPUT_DIR)
            os.remove(tar_file)
            print(f"✅ Successfully extracted {os.path.basename(tar_file)}")
        except Exception as e:
            print(f"❌ Extraction failed for {os.path.basename(tar_file)}: {str(e)}")

def check_expected_count(df):
    """Check if the output folder contains the expected number of files."""
    print("\n🔢 Validating file counts...")
    df["expected_count"] = df["download_ID"].apply(
        lambda x: "worked" if (
            x != "failed" and 
            os.path.exists(os.path.join(OUTPUT_DIR, x)) and 
            len(os.listdir(os.path.join(OUTPUT_DIR, x))) >= EXPECTED_FILES_COUNT
        ) else "failed"
    )

def validate_final_status(df):
    """Calculate final validation status."""
    print("\n✅ Final validation...")
    status_columns = ["download_ID", "view_links", "download_links", "expected_count"]
    df["valid_download"] = df.apply(
        lambda row: "worked" if all(row[col] != "failed" for col in status_columns) else "failed",
        axis=1
    )

if __name__ == "__main__":
    combined_df = process_csv_files()
    
    download_tar_gz_files(combined_df)
    extract_tar_gz_files()
    
    check_expected_count(combined_df)
    validate_final_status(combined_df)

    final_columns = [
        'download_ID', 'view_links', 'download_links', 'expected_count', 'valid_download'
    ]
    final_df = combined_df[final_columns].copy()
    
    final_df.to_csv(FINAL_CSV, index=False)
    print(f"\n🎉 Final results saved to: {FINAL_CSV}")

    print("\n📊 Overall Validation Summary:")
    print(final_df[['valid_download', 'download_ID']].groupby('valid_download').count())

    print("\n✅ Processing complete!")

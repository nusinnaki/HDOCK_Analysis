import glob
import os
import tarfile
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Global base URL for HDOCK
BASE_URL = "http://hdock.phys.hust.edu.cn/data/"

def extract_job_id(html):
    """
    Parses the HTML and extracts the job ID from the <title> tag.
    Expected title format:
      <title> HDOCK Server: Job results for 67c074b475cea</title>
    Returns the job ID (e.g., "67c074b475cea") if found; otherwise, returns "failed".
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            text = title_tag.get_text(strip=True)
            if "HDOCK Server: Job results for" in text:
                parts = text.split("for")
                if len(parts) > 1:
                    return parts[-1].strip().split()[0]
        return "failed"
    except Exception:
        return "failed"
def process_csv_files(directory):
    """
    Processes all CSV files in the given directory whose names start with "responses".
    For each CSV:
      - Reads the CSV into a DataFrame.
      - Extracts the job ID from the "Response" column.
      - Generates two new columns: "view_links" and "download_links".
      - Uses "failed" if extraction is unsuccessful.
    All processed DataFrames are concatenated and returned.
    """
    csv_files = glob.glob(os.path.join(directory, "responses*.csv"))
    if not csv_files:
        print("No CSV files found starting with 'responses' in", directory)
        return pd.DataFrame()

    df_list = []
    for file in csv_files:
        df = pd.read_csv(file)
        # Extract job IDs from the "Response" column.
        df["download_ID"] = df["Response"].apply(lambda x: extract_job_id(x) if isinstance(x, str) else "failed")
        # Create the view and download links.
        df["view_links"] = df["download_ID"].apply(lambda x: f"{BASE_URL}{x}/" if x != "failed" else "failed")
        df["download_links"] = df["download_ID"].apply(lambda x: f"{BASE_URL}{x}/all_results.tar.gz" if x != "failed" else "failed")
        df_list.append(df)
    
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

def download_tar_gz_files(df, output_directory):
    """
    Downloads all tar.gz files listed in the DataFrame's "download_links" column.
    Files are saved to output_directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print("Created download directory:", output_directory)
    
    for index, row in df.iterrows():
        url = row["download_links"]
        job_id = row["download_ID"]
        if url == "failed" or job_id == "failed":
            print(f"Skipping row {index} due to failed job ID or URL.")
            continue
        
        file_name = f"{job_id}.tar.gz"
        file_path = os.path.join(output_directory, file_name)
        
        # Skip download if file already exists.
        if os.path.exists(file_path):
            print(f"{file_name} already exists, skipping download.")
            continue
        
        try:
            print(f"Downloading {file_name} from {url}...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded {file_name}")
            else:
                print(f"Failed to download {url} (status code: {response.status_code}).")
        except Exception as e:
            print(f"Exception occurred while downloading {url}: {e}")

def extract_tar_gz_files(output_directory):
    """
    Extracts all tar.gz files in the given output_directory.
    After successful extraction, deletes the tar.gz file.
    """
    tar_files = glob.glob(os.path.join(output_directory, "*.tar.gz"))
    for tar_file in tar_files:
        try:
            print(f"Extracting {os.path.basename(tar_file)}...")
            with tarfile.open(tar_file, "r:gz") as tar:
                tar.extractall(path=output_directory)
            print(f"Extracted {os.path.basename(tar_file)}")
            # Delete the tar.gz file after extraction.
            os.remove(tar_file)
            print(f"Deleted {os.path.basename(tar_file)} after extraction.")
        except Exception as e:
            print(f"Failed to extract {tar_file}: {e}")

if __name__ == "__main__":
    # Directory containing your CSV files
    csv_directory = "/Users/nusin/Desktop/Hdock_responses"
    # Directory to store downloaded tar.gz files and their extracted contents
    download_directory = os.path.join(csv_directory, "hdock_output")

    # Process CSV files and write the combined DataFrame to a CSV.
    combined_df = process_csv_files(csv_directory)
    output_csv = os.path.join(csv_directory, "download_responses.csv")
    combined_df.to_csv(output_csv, index=False)
    print("CSV output written to:", output_csv)

    # First, download all tar.gz files.
    download_tar_gz_files(combined_df, download_directory)
    
    # Once all files are downloaded, extract them and delete the original tar.gz files.
    extract_tar_gz_files(download_directory)

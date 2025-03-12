import re
import asyncio
import aiohttp
import pandas as pd
import warnings
import unicodedata  # To normalize Unicode characters

# ============================================================
# Configuration Variables (Edit these as needed)
# ============================================================
LIGAND_EXCEL_FILE_PATH = "/Users/nusin/Library/Mobile Documents/com~apple~CloudDocs/Desktop/IOV/3_Projects/PPI/0_Proteins_of_Interest/list of 75 proteins of interest.xlsx"
OUTPUT_CSV_FILE_PATH = "/Users/nusin/Library/Mobile Documents/com~apple~CloudDocs/Desktop/IOV/3_Projects/PPI/1_Input_Proteins_pdbs/df_all_ligands.csv"
CONCURRENT_TASKS_LIMIT = 10
TIMEOUT = 10  # Seconds

# Base URLs for external APIs
UNIPROT_FASTA_BASE_URL = "https://www.uniprot.org/uniprot"
UNIPROT_JSON_BASE_URL = "https://rest.uniprot.org/uniprotkb"
RCSB_QUERY_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_ENTRY_BASE_URL = "https://data.rcsb.org/rest/v1/core/entry"
RCSB_POLYMER_ENTITY_BASE_URL = "https://data.rcsb.org/rest/v1/core/polymer_entity"
# ============================================================

# (Optional) Suppress openpyxl conditional formatting warning
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# -----------------------------
# Step 1. Load and clean ligand data from the Excel file
# -----------------------------
ligand_df = pd.read_excel(LIGAND_EXCEL_FILE_PATH)
ligand_df.columns = ligand_df.columns.str.strip()
ligand_df['Accession'] = ligand_df['Accession'].str.replace(r'-1$', '', regex=True)

# -----------------------------
# Step 2. Define async functions to fetch UniProt data
# -----------------------------
async def get_uniprot_sequence(accession, session):
    """Fetch the protein sequence in FASTA format and return its length."""
    uniprot_url = f"{UNIPROT_FASTA_BASE_URL}/{accession}.fasta"
    try:
        async with session.get(uniprot_url, timeout=TIMEOUT) as response:
            if response.status == 200:
                fasta_data = await response.text()
                # Skip header and join the remaining lines
                sequence = "".join(fasta_data.splitlines()[1:])
                return len(sequence)
            else:
                print(f"Failed to fetch FASTA for {accession}, Status code: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching FASTA for {accession}: {e}")
        return None

async def get_uniprot_json_data(accession, session):
    """Fetch the UniProt JSON data for additional protein details."""
    url = f"{UNIPROT_JSON_BASE_URL}/{accession}?format=json"
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch JSON data for {accession}, Status code: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching JSON data for {accession}: {e}")
        return None

# -----------------------------
# Step 3. Define an async function to process one ligand
# -----------------------------
async def process_ligand(session, row):
    results_list = []
    # Use ligand_df values as defaults
    accession = row["Accession"]
    gene_symbol = row["Gene Symbol"]
    ensembl_gene_id = row["Ensembl Gene ID"]
    pfam_ids = row["Pfam IDs"]

    print(f"Processing {accession}...")

    # Get sequence length
    seq_length = await get_uniprot_sequence(accession, session)
    if seq_length is None:
        # Without sequence length, add a result row with N/A
        results_list.append({
            "protein_name": "N/A",
            "short_name": "N/A",
            "gene_symbol": gene_symbol,
            "gene_ID": ensembl_gene_id,
            "accession": accession,
            "pfam_ID": pfam_ids,
            "identifier": "N/A",
            "method": "N/A",
            "resolution": "N/A",
            "chain": "N/A",
            "sequence_length": "N/A",
            "positions": "N/A"
        })
        return results_list

    # Get UniProt JSON data to fetch protein_name and short_name (and optionally update gene_symbol, gene_ID, pfam_ID)
    uniprot_json = await get_uniprot_json_data(accession, session)
    if uniprot_json:
        protein_description = uniprot_json.get("proteinDescription", {})
        recommended_name = protein_description.get("recommendedName", {})
        protein_name = recommended_name.get("fullName", {}).get("value", "N/A")
        short_names = recommended_name.get("shortNames", [])
        short_name = short_names[0]["value"] if short_names else "N/A"
        # Update gene symbol if available
        genes = uniprot_json.get("genes", [])
        gene_symbol = genes[0].get("geneName", {}).get("value", gene_symbol) if genes else gene_symbol

        # Extract Ensembl gene ID and Pfam IDs from cross-references
        ensembl_gene_id_new = "N/A"
        pfam_ids_new = []
        cross_refs = uniprot_json.get("uniProtKBCrossReferences", [])
        for ref in cross_refs:
            if ref.get("database") == "Ensembl":
                for prop in ref.get("properties", []):
                    if prop.get("key") == "gene":
                        ensembl_gene_id_new = prop.get("value")
                        break
                if ensembl_gene_id_new == "N/A":
                    ensembl_gene_id_new = ref.get("id", "N/A")
            if ref.get("database") == "Pfam":
                pfam_ids_new.append(ref.get("id"))
        pfam_ids_new = ", ".join(pfam_ids_new) if pfam_ids_new else pfam_ids
        ensembl_gene_id = ensembl_gene_id_new if ensembl_gene_id_new != "N/A" else ensembl_gene_id
        pfam_ids = pfam_ids_new
    else:
        protein_name = "N/A"
        short_name = "N/A"

    # Build the JSON query for experimental structures from RCSB
    query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                        "operator": "exact_match",
                        "value": accession
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name",
                        "operator": "exact_match",
                        "value": "UniProt"
                    }
                }
            ]
        },
        "return_type": "entry",
        "request_options": {"return_all_hits": True}
    }
    # Use the configured RCSB query URL
    rcsb_query_url = RCSB_QUERY_URL
    
    try:
        async with session.post(rcsb_query_url, json=query, timeout=TIMEOUT) as response:
            text = await response.text()
            if not text.strip():
                print(f"Empty response for accession {accession}. Skipping experimental structures.")
                # Add a row for RCSB with N/A values
                results_list.append({
                    "protein_name": protein_name,
                    "short_name": short_name,
                    "gene_symbol": gene_symbol,
                    "gene_ID": ensembl_gene_id,
                    "accession": accession,
                    "pfam_ID": pfam_ids,
                    "identifier": "rcsb",
                    "method": "N/A",
                    "resolution": "N/A",
                    "chain": "N/A",
                    "sequence_length": seq_length,
                    "positions": "N/A"
                })
            else:
                result = await response.json()
                # For each entry, normalize the identifier and only accept if it exactly matches 4 alphanumeric characters.
                pdb_ids = []
                for entry in result.get("result_set", []):
                    raw_id = entry["identifier"]
                    normalized = unicodedata.normalize("NFKC", raw_id).strip()
                    if re.fullmatch(r"[A-Za-z0-9]{4}", normalized):
                        pdb_ids.append(normalized.upper())

                if not pdb_ids:
                    print(f"No valid PDB IDs found for {accession}.")
                    results_list.append({
                        "protein_name": protein_name,
                        "short_name": short_name,
                        "gene_symbol": gene_symbol,
                        "gene_ID": ensembl_gene_id,
                        "accession": accession,
                        "pfam_ID": pfam_ids,
                        "identifier": "rcsb",
                        "method": "N/A",
                        "resolution": "N/A",
                        "chain": "N/A",
                        "sequence_length": seq_length,
                        "positions": "N/A"
                    })
                else:
                    # Process each experimental structure
                    for pdb_id in pdb_ids:
                        pdb_url = f"{RCSB_ENTRY_BASE_URL}/{pdb_id}"
                        try:
                            async with session.get(pdb_url, timeout=TIMEOUT) as pdb_response:
                                pdb_data = await pdb_response.json()
                                method = pdb_data.get("rcsb_entry_info", {}).get("experimental_method", "N/A")
                                resolution_list = pdb_data.get("rcsb_entry_info", {}).get("resolution_combined", ["N/A"])
                                resolution = resolution_list[0]
                                if resolution != "N/A":
                                    resolution = f"{resolution} Å"

                                polymer_entities = pdb_data.get("rcsb_entry_container_identifiers", {}).get("polymer_entity_ids", [])
                                all_chains = []
                                for entity_id in polymer_entities:
                                    entity_url = f"{RCSB_POLYMER_ENTITY_BASE_URL}/{pdb_id}/{entity_id}"
                                    try:
                                        async with session.get(entity_url, timeout=TIMEOUT) as entity_response:
                                            entity_data = await entity_response.json()
                                            chain_list = entity_data.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_ids", [])
                                            if chain_list:
                                                all_chains.extend(chain_list)
                                    except Exception as e:
                                        print(f"Error fetching polymer entity {entity_id} for {pdb_id}: {e}")
                                        continue
                                chain = "/".join(all_chains) if all_chains else "N/A"
                                positions_range = f"1-{seq_length}"
                                
                                results_list.append({
                                    "protein_name": protein_name,
                                    "short_name": short_name,
                                    "gene_symbol": gene_symbol,
                                    "gene_ID": ensembl_gene_id,
                                    "accession": accession,
                                    "pfam_ID": pfam_ids,
                                    "identifier": pdb_id,
                                    "method": method,
                                    "resolution": resolution,
                                    "chain": chain,
                                    "sequence_length": seq_length,
                                    "positions": positions_range
                                })
                        except Exception as e:
                            print(f"Error fetching PDB details for {pdb_id}: {e}")
                            continue
    except Exception as e:
        print(f"Error querying RCSB for {accession}: {e}")
        results_list.append({
            "protein_name": protein_name,
            "short_name": short_name,
            "gene_symbol": gene_symbol,
            "gene_ID": ensembl_gene_id,
            "accession": accession,
            "pfam_ID": pfam_ids,
            "identifier": "rcsb",
            "method": "N/A",
            "resolution": "N/A",
            "chain": "N/A",
            "sequence_length": seq_length,
            "positions": "N/A"
        })

    # Add the AlphaFold predicted structure row for this accession
    alphafold_id = f"AF-{accession}-F1"
    try:
        results_list.append({
            "protein_name": protein_name,
            "short_name": short_name,
            "gene_symbol": gene_symbol,
            "gene_ID": ensembl_gene_id,
            "accession": accession,
            "pfam_ID": pfam_ids,
            "identifier": alphafold_id,
            "method": "Predicted",
            "resolution": "",
            "chain": "",
            "sequence_length": seq_length,
            "positions": ""
        })
    except Exception as e:
        print(f"Error adding AlphaFold structure for {accession}: {e}")
        results_list.append({
            "protein_name": protein_name,
            "short_name": short_name,
            "gene_symbol": gene_symbol,
            "gene_ID": ensembl_gene_id,
            "accession": accession,
            "pfam_ID": pfam_ids,
            "identifier": "alphafold",
            "method": "N/A",
            "resolution": "N/A",
            "chain": "N/A",
            "sequence_length": seq_length,
            "positions": "N/A"
        })
    
    return results_list

# -----------------------------
# Wrap process_ligand with a semaphore to limit concurrent tasks
# -----------------------------
async def sem_process_ligand(semaphore, session, row):
    async with semaphore:
        return await process_ligand(session, row)

# -----------------------------
# Step 4. Process all ligands concurrently
# -----------------------------
async def fetch_ligand_structures():
    all_results = []
    semaphore = asyncio.Semaphore(CONCURRENT_TASKS_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [sem_process_ligand(semaphore, session, row) for _, row in ligand_df.iterrows()]
        ligands_results = await asyncio.gather(*tasks)
        for result in ligands_results:
            all_results.extend(result)
    return all_results

# -----------------------------
# Step 5. Main async function to get data and save results
# -----------------------------
async def main():
    ligand_results = await fetch_ligand_structures()
    columns = [
        "protein_name", "short_name", "gene_symbol", "gene_ID", "accession", 
        "pfam_ID", "identifier", "method", "resolution", "chain", "sequence_length", "positions"
    ]
    df_ligand_structures = pd.DataFrame(ligand_results, columns=columns)
    print(df_ligand_structures.head())
    df_ligand_structures.to_csv(OUTPUT_CSV_FILE_PATH, index=False)
    print(f"Saved ligand structures to {OUTPUT_CSV_FILE_PATH}")

# -----------------------------
# Run the async main function
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())

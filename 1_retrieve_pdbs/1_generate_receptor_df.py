import os
import requests
import pandas as pd

# ============================================================
# Configuration Variables (Edit these as needed)
# ============================================================
OUTPUT_DIR = "/Users/nusin/Library/Mobile Documents/com~apple~CloudDocs/Desktop/IOV/3_Projects/PPI/1_Input_Proteins_pdbs"
OUTPUT_FILENAME = "df_receptor_HO-1.csv"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
# ============================================================

def get_uniprot_sequence_length(accession):
    """
    Fetch the protein sequence from UniProt in FASTA format and return its length.
    """
    uniprot_url = f"https://www.uniprot.org/uniprot/{accession}.fasta"
    try:
        response = requests.get(uniprot_url, timeout=10)
        if response.status_code == 200:
            fasta_data = response.text
            # Skip the header (first line) and join the remaining lines
            sequence = "".join(fasta_data.splitlines()[1:])
            return len(sequence)
        else:
            print(f"Failed to fetch UniProt FASTA data for {accession}, Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching UniProt FASTA data for {accession}: {e}")
        return None

# Define the two UniProt accession codes
uniprot_accessions = ["P09601", "A0A7I2V3I1"]

# Define DataFrame columns including the new "sequence_length" column before "positions"
columns = [
    "protein_name", "short_name", "gene_symbol", "gene_ID", "accession", 
    "pfam_ID", "identifier", "method", "resolution", "chain", "sequence_length", "positions"
]
df = pd.DataFrame(columns=columns)

# Loop over each UniProt accession
for uniprot_accession in uniprot_accessions:
    # Retrieve protein info from the UniProt REST API
    uniprot_url = f"https://rest.uniprot.org/uniprotkb/{uniprot_accession}?format=json"
    uniprot_response = requests.get(uniprot_url)
    if uniprot_response.status_code == 200:
        uniprot_data = uniprot_response.json()
        
        # Extract full protein name and short name from the recommendedName field
        protein_description = uniprot_data.get("proteinDescription", {})
        recommended_name = protein_description.get("recommendedName", {})
        protein_name = recommended_name.get("fullName", {}).get("value", "N/A")
        short_names = recommended_name.get("shortNames", [])
        short_name = short_names[0]["value"] if short_names else "N/A"
        
        # Extract gene symbol from the "genes" field
        genes = uniprot_data.get("genes", [])
        gene_symbol = genes[0].get("geneName", {}).get("value", "N/A") if genes else "N/A"
        
        # Extract Ensembl gene ID and Pfam IDs from the cross-references
        ensembl_gene_id = "N/A"
        pfam_ids = []
        cross_refs = uniprot_data.get("uniProtKBCrossReferences", [])
        for ref in cross_refs:
            if ref.get("database") == "Ensembl":
                # Look for the property with key "gene"
                for prop in ref.get("properties", []):
                    if prop.get("key") == "gene":
                        ensembl_gene_id = prop.get("value")
                        break
                # Fallback: if not found, use the reference ID
                if ensembl_gene_id == "N/A":
                    ensembl_gene_id = ref.get("id", "N/A")
            if ref.get("database") == "Pfam":
                pfam_ids.append(ref.get("id"))
        pfam_ids = ", ".join(pfam_ids) if pfam_ids else "N/A"
    else:
        protein_name = "N/A"
        short_name = "N/A"
        gene_symbol = "N/A"
        ensembl_gene_id = "N/A"
        pfam_ids = "N/A"
    
    # Get the sequence length from the UniProt FASTA file
    sequence_length = get_uniprot_sequence_length(uniprot_accession)
    
    # Build the JSON query to get PDB IDs for experimental structures from RCSB
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
                        "value": uniprot_accession
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
    
    # URL for the RCSB search API
    rcsb_url = "https://search.rcsb.org/rcsbsearch/v2/query"
    
    # Send the POST request to RCSB
    response = requests.post(rcsb_url, json=query)
    if response.status_code == 200:
        results = response.json()
        pdb_ids = [entry["identifier"] for entry in results.get("result_set", [])]
    
        # Process experimental structures for this accession
        for pdb_id in pdb_ids:
            pdb_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            pdb_response = requests.get(pdb_url)
            if pdb_response.status_code == 200:
                pdb_data = pdb_response.json()
                method = pdb_data.get("rcsb_entry_info", {}).get("experimental_method", "N/A")
                # Extract resolution using the "resolution_combined" field
                resolution = pdb_data.get("rcsb_entry_info", {}).get("resolution_combined", ["N/A"])[0]
                if resolution != "N/A":
                    resolution = f"{resolution} Å"
    
                polymer_entities = pdb_data.get("rcsb_entry_container_identifiers", {}).get("polymer_entity_ids", [])
                for entity_id in polymer_entities:
                    entity_url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/{entity_id}"
                    entity_response = requests.get(entity_url)
                    if entity_response.status_code == 200:
                        entity_data = entity_response.json()
                        # Concatenate chain IDs with '/'
                        chain = "/".join(entity_data.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_ids", []))
                        # Use the length of the canonical sequence (if available) as a proxy for Positions
                        seq = entity_data.get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "N/A")
                        positions_range = f"1-{len(seq)}" if seq != "N/A" else "N/A"
    
                        new_row = pd.DataFrame({
                            "protein_name": [protein_name],
                            "short_name": [short_name],
                            "gene_symbol": [gene_symbol],
                            "gene_ID": [ensembl_gene_id],
                            "accession": [uniprot_accession],
                            "pfam_ID": [pfam_ids],
                            "identifier": [pdb_id],
                            "method": [method],
                            "resolution": [resolution],
                            "chain": [chain],
                            "sequence_length": [sequence_length],
                            "positions": [positions_range]
                        })
                        df = pd.concat([df, new_row], ignore_index=True)
    else:
        print(f"Error {response.status_code}: {response.text}")
    
    # Now add the AlphaFold predicted structure row for this accession
    alphafold_id = f"AF-{uniprot_accession}-F1"
    alphafold_url = f"https://alphafold.ebi.ac.uk/files/{alphafold_id}.pdb"
    alphafold_method = "Predicted"
    alphafold_resolution = ""
    alphafold_chain = ""
    alphafold_positions = ""
    
    af_response = requests.get(alphafold_url)
    if af_response.status_code == 200:
        # Optionally add parsing logic for the AlphaFold structure if needed
        pass
    
    new_row_af = pd.DataFrame({
        "protein_name": [protein_name],
        "short_name": [short_name],
        "gene_symbol": [gene_symbol],
        "gene_ID": [ensembl_gene_id],
        "accession": [uniprot_accession],
        "pfam_ID": [pfam_ids],
        "identifier": [alphafold_id],
        "method": [alphafold_method],
        "resolution": [alphafold_resolution],
        "chain": [alphafold_chain],
        "sequence_length": [sequence_length],
        "positions": [alphafold_positions]
    })
    df = pd.concat([df, new_row_af], ignore_index=True)

# Display the final DataFrame
print(df)

# Save the DataFrame to CSV using the dynamically generated output path
df.to_csv(OUTPUT_PATH, index=False)
print(f"Data saved to {OUTPUT_PATH}")

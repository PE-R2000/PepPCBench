import argparse
import requests
import json
import os
import csv
import requests

def separate_nmr_static(cif_file_path):

    pdb_id = os.path.basename(cif_file_path).split('.')[0]
    url = f'https://data.rcsb.org/rest/v1/core/entry/{pdb_id}'

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            return {"error": f"PDB ID '{pdb_id}' not found"}
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch data for PDB ID '{pdb_id}' with status code {response.status_code}"}
        
        data = response.json()

        experimental_method = data.get("rcsb_entry_info", {}).get("experimental_method")

        if not experimental_method:
            return {"error": "Experimental method not found in API response"}

        return {"pdb_id": pdb_id, "experimental_method": experimental_method}

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main(cif_folder_path):

    for files in os.listdir(cif_folder_path):
        if files.endswith(".cif"):
            cif_file_path = os.path.join(cif_folder_path, files)
            result = separate_nmr_static(cif_file_path)

            if "error" in result:
                print(result["error"])
                continue  # Skip to next file

            if "NMR" in result["experimental_method"]:
                parent_folder = os.path.dirname(cif_file_path)
                nmr_folder = os.path.join(parent_folder, "NMR")
                os.makedirs(nmr_folder, exist_ok=True)
                dest_path = os.path.join(nmr_folder, os.path.basename(cif_file_path))
                os.rename(cif_file_path, dest_path)
                print(f"Moved '{cif_file_path}' to '{dest_path}'")
            else:
                parent_folder = os.path.dirname(cif_file_path)
                static_folder = os.path.join(parent_folder, "Static")
                os.makedirs(static_folder, exist_ok=True)
                dest_path = os.path.join(static_folder, os.path.basename(cif_file_path))
                os.rename(cif_file_path, dest_path)
                print(f"Moved '{cif_file_path}' to '{dest_path}'")

main('/home/aethercore/Doutoramento/PepBench_dataset/Dataset_curation/pdb_test_data')
import pandas as pd
from pathlib import Path
import shutil
from tqdm import tqdm
import os
import requests
import concurrent.futures

# Define a function to get the cif file path by pdb_id
def get_cif_by_pdb_id(pdb_id):
    subdir = pdb_id[1:3]
    cif_path = mmcif_dir / subdir / f"{pdb_id}.cif.gz"
    return cif_path

def download_single_cif(pdb_id, pdb_data_dir):
    url = f"https://files.rcsb.org/download/{pdb_id}-assembly1.cif" #Add -assembly1.cif if using static structures
    try:
        response = requests.get(url)
        if response.status_code == 200:
            cif_path = pdb_data_dir / f"{pdb_id.lower()}.cif"
            with open(cif_path, 'wb') as f:
                f.write(response.content)
            return (pdb_id, True)
        else:
            print(f"Failed to download {url}")
            return (pdb_id, False)
    except Exception as e:
        print(f"Error downloading {pdb_id}: {e}")
        return (pdb_id, False)

def download_cif(df, pdb_data_dir, max_workers=8):
    success_num = 0
    error_num = 0
    error_list = []

    pdb_ids = df.pdb_id.tolist()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(lambda pid: download_single_cif(pid, pdb_data_dir), pdb_ids), total=len(pdb_ids)))
        for pdb_id, success in results:
            if success:
                success_num += 1
            else:
                error_num += 1
                error_list.append(pdb_id)

    print(f"Success count: {success_num}")
    print(f"Error count: {error_num}")
    if error_list:
        print("Errors occurred for the following pdb_ids:")
        print(error_list)

    return success_num, error_num, error_list

def get_cif(df, pdb_data_dir, mmcif_dir):

    for _pdb_id in tqdm(df.pdb_id):
            pdb_id = _pdb_id.lower()
            try:
                # Source and destination paths
                source_path = get_cif_by_pdb_id(pdb_id)
                destination_path = pdb_data_dir / source_path.name
                
                # Check if the file already exists
                if destination_path.exists():
                    success_num += 1  # Count as success if file exists
                    continue
                
                # Copy file if it doesn't exist
                shutil.copy(source_path, destination_path)
                success_num += 1
            except Exception as e:
                print(f"{pdb_id} failed to copy. Error: {e}")
                error_num += 1
                error_list.append(pdb_id)

                # Print results
                print(f"Success count: {success_num}")
                print(f"Error count: {error_num}")
                if error_list:
                    print("Errors occurred for the following pdb_ids:")
                    print(error_list)

    return success_num, error_num, error_list

def build_pdb_data(df, pdb_data_dir, mmcif_dir = None):

    if mmcif_dir is None:
        success_num, error_num, error_list = download_cif(df, pdb_data_dir)
    
    else:
        success_num, error_num, error_list = get_cif(df, pdb_data_dir, mmcif_dir)

    return success_num, error_num, error_list
        

if __name__ == "__main__":
    # Load the CSV file
    df = pd.read_csv("/home/aethercore/PepPCBench/clusters/true_static_training_boltz.csv")

    # Create the output directory
    pdb_data_dir = Path("/home/aethercore/Doutoramento/PepBench_dataset/Dataset_curation/pdb_data/Static")
    pdb_data_dir.mkdir(exist_ok=True)

    # Define the source mmCIF directory
    # mmcif_dir = Path("~/data/alphafold/mmCIF").expanduser()

    success_num, error_num, error_list = build_pdb_data(df, pdb_data_dir, mmcif_dir=None)


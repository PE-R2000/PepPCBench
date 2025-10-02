import requests
import json
from datetime import datetime
import os
import csv

def pdb_release_date(pdb_id):
    """
    Get release date information for a given PDB ID.
    """
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return {"error": f"PDB ID '{pdb_id}' not found"}
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch data for PDB ID '{pdb_id}' with status code {response.status_code}"}
        
        data = response.json()
        
        release_date = data.get("rcsb_accession_info", {}).get("initial_release_date")
        
        if not release_date:
            return {"error": "Release date not found in API response"}
        
        release_datetime = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
        return {"pdb_id": pdb_id, "release_datetime_obj": release_datetime.replace(tzinfo=None)}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def filter_csv_by_release_date(csv_path, cutoff_date, output_csv):
    """
    Reads a CSV file with PDB IDs, removes those below the cutoff date, and writes the filtered list to a new CSV.
    """
    cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d")
    filtered_rows = []
    removed_rows = []
    
    with open(csv_path, newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    print(f"Processing {len(rows)} PDB IDs from {csv_path}...")
    
    for i, row in enumerate(rows, 1):
        pdb_id = row['pdb_id']
        print(f"[{i}/{len(rows)}] Checking {pdb_id}...", end=" ")
        result = pdb_release_date(pdb_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            removed_rows.append(row)
            continue
        
        release_date = result["release_datetime_obj"]
        if release_date >= cutoff:
            print(f"✅ Kept (released {release_date.strftime('%Y-%m-%d')})")
            filtered_rows.append(row)
        else:
            print(f"⏭️  Removed (released {release_date.strftime('%Y-%m-%d')})")
            removed_rows.append(row)
    
    # Write filtered rows to output CSV
    with open(output_csv, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)
    
    print("-" * 80)
    print(f"Summary:")
    print(f"  Total PDB IDs: {len(rows)}")
    print(f"  Kept: {len(filtered_rows)}")
    print(f"  Removed: {len(removed_rows)}")
    print(f"Filtered CSV written to {output_csv}")

if __name__ == "__main__":
    # Example usage
    csv_path = "/home/aethercore/PepPCBench/job_list.csv"
    output_csv = "/home/aethercore/PepPCBench/job_list_updated.csv"
    cutoff_date = "2023-06-01"  # Change this to your desired cutoff date
    filter_csv_by_release_date(csv_path, cutoff_date, output_csv)
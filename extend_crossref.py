# This script extends the crossref 2023 public data file to include records from 2024. 
# The file is over 170 GiB, so it is not included in the repo, but you can easily torrent it from
# https://academictorrents.com/details/d9e554f4f0c3047d9f49e448a7004f7aa1701b69 

import requests
import json
import os
import gzip
import sys

def fetch_entries(cursor) -> requests.Response:
    url = "https://api.crossref.org/works"
    query_params = {
        'filter': 'from-index-date:2023-04-01', 
        'rows': 1000,
        'cursor': cursor
    }
    headers = {
        'Mailto': 'nandajafarian99@gmail.com'
    }
    
    response = requests.get(url, params=query_params, headers=headers)
    
    return response

def save_entries(items, file_number) -> None:
    directory = "./data/crossref_data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = f"{directory}/{file_number}.json.gz"
    with gzip.open(file_path, 'wt', encoding="UTF-8") as zipfile:
        json.dump({"items": items}, zipfile, indent=4)
    print(f"Data successfully saved to: {file_path}")



def main():
    initial_cursor = "*"
    file_number = 1
    
    while True:
        response = fetch_entries(cursor=initial_cursor)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['message']['items']:
                save_entries(data['message']['items'], file_number)
                file_number += 1
                initial_cursor = data['message']['next-cursor']
            else:
                print("No more data available.")
                break
        else:
            print("Failed to fetch data:", response.status_code)
            break

if __name__ == "__main__":
    main()
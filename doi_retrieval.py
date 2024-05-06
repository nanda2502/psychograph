from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import gzip
import json
import os

def read_and_filter_data(file_path, target_journals):
    """ Read a .json.gz file, parse JSON data, and filter DOIs based on target journals """
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from {file_path}")
        return []
    except OSError:
        print(f"Could not open/read file: {file_path}")
        return []

    dois = []
    for item in data.get("items", []):
        journal_titles = set(item.get("container-title", []) + item.get("short-container-title", []))
        if any(journal in journal_titles for journal in target_journals):
            doi = item.get("DOI")
            if doi:
                dois.append(doi)
    return dois

def process_files(directory, target_journals):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json.gz')]
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() - 1) as executor:
        tasks = [(file, target_journals) for file in files]
        results = list(executor.map(lambda p: read_and_filter_data(*p), tasks))

    all_dois = [doi for sublist in results for doi in sublist]
    return all_dois

def save_dois_to_text_file(dois, filename):
    with open(filename, "w") as file:
        for doi in dois:
            file.write(doi + "\n")

def read_target_journals(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def main():
    directory = "./data/crossref/"
    target_journals_file = "./data/target_journals.txt"
    output_file = "./data/dois.txt"
    
    target_journals = read_target_journals(target_journals_file)
    
    all_dois = process_files(directory, target_journals)

    save_dois_to_text_file(all_dois, output_file)
    
    print(f"Processed {len(all_dois)} DOIs matching the target journals. Results saved to {output_file}.")

if __name__ == '__main__':
    main()
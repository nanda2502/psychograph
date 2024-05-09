from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import gzip
import json
import os
import time
import csv
import pickle
import re

def read_and_filter_data(file_path, keywords, start_year, end_year, use_all = False) -> tuple[list[str], list[tuple[str, str]], dict[str, tuple[str, list[str]]]]:
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error opening or reading file: {file_path}, {str(e)}")
        return []

    dois = []
    edges = []
    metadata = {}

    for item in data.get("items", []):
        if item.get("type") != "journal-article":
            continue

        journal_titles = set(item.get("container-title", []) + item.get("short-container-title", []))
        if use_all or any(keyword.lower() in title.lower() for title in journal_titles for keyword in keywords):
            try:
                date_parts = item.get("published", {}).get("date-parts", [[None]])
                publication_year = date_parts[0][0] if date_parts and date_parts[0] else None
                if publication_year is None:
                    raise ValueError("Date-parts is missing or incorrectly formatted.")
            except (IndexError, ValueError) as e:
                print(f"Warning: Could not extract publication year for DOI: {item.get('DOI', 'Unknown')}: {str(e)}")
                continue

            if use_all or publication_year and int(start_year) <= int(publication_year) <= int(end_year):
                if use_all or any(journal in journal_titles for journal in keywords):
                    doi = item.get("DOI")
                    title = item.get("title", [""])[0]
                    subjects = item.get("subject", [])
                    if doi:
                        dois.append(doi)
                        metadata[doi] = (title, subjects, publication_year)
                        for ref in item.get("reference", []):
                            ref_doi = ref.get("DOI")
                            ref_year = ref.get("year")
                            if ref_doi and ref_year:
                                match = re.search(r'\d{4}', ref_year)
                                if match:
                                    ref_year_clean = int(match.group())
                                    if start_year <= ref_year_clean <= end_year:
                                        metadata[ref_doi] = ("", "", ref_year_clean)
                                        edges.append((doi, ref_doi))
    return dois, edges, metadata

def helper_task(params) -> tuple[list[str], list[str]]:
    return read_and_filter_data(*params)

def process_files(directory: str, keywords: list[str], start_year: int, end_year: int, use_all: bool = False):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json.gz')]
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        tasks = [(file, keywords, start_year, end_year, use_all) for file in files]
        results = list(executor.map(helper_task, tasks))

    all_dois = [doi for sublist in results for doi in sublist[0]]
    all_edges = [edge for sublist in results for edge in sublist[1]]
    flattened_edges = [edge for sublist in all_edges for edge in sublist]
    metadata = {doi: info for sublist in results for doi, info in sublist[2].items()}
    return all_dois, flattened_edges, metadata

def save_dois_to_text_file(dois, filename) -> None:
    with open(filename, "w") as file:
        for doi in dois:
            file.write(doi + "\n")

def save_edges_to_csv_file(edges, filename) -> None:
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(edges)

def read_keywords(filename, encoding = "utf-8") -> list[str]:
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def read_target_years(filename) -> tuple[str, str]:
    with open(filename, "r") as file:
        start = file.readline().strip()
        end = file.readline().strip()
    return start, end

def pickle_metadata(metadata, filename) -> None:
    with open(filename, 'wb') as file:
        pickle.dump(metadata, file)

def main():
    time_start = time.time()
    directory = "./crossref_data/"
    keywords_file = "./data/keywords.txt"
    output_file_dois = "./data/dois.txt"
    output_file_edges = "./data/edges.csv"
    output_file_metadata = "./data/metadata.pkl"
    
    keywords = read_keywords(keywords_file)
    start_year = 1
    end_year = 2024
    
    all_dois, edges, metadata = process_files(directory, keywords, int(start_year), int(end_year), use_all = True)

    save_dois_to_text_file(all_dois, output_file_dois)
    save_edges_to_csv_file(edges, output_file_edges)
    pickle_metadata(metadata, output_file_metadata)
    time_end = time.time()
    
    print(f"Processed {len(all_dois)} DOIs matching the target journals. Results saved to {output_file_dois} and {output_file_edges}. \n Total time: {time_end - time_start:.2f} seconds.")

if __name__ == '__main__':
    main()
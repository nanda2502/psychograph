from openai import AsyncOpenAI
import gzip
import json
import asyncio
import re
from concurrent.futures import ProcessPoolExecutor
import os
client = AsyncOpenAI()

def get_journals_crossref(file_path):
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from {file_path}")
        return []
    except OSError:
        print(f"Could not open/read file: {file_path}")
        return []

    journal_titles = set()
    for item in data.get("items", []):
        journal_titles.update(item.get("container-title", []))
        journal_titles.update(item.get("short-container-title", []))

    return list(journal_titles)

def process_files(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.gz')]
    journal_titles = set()
    with ProcessPoolExecutor() as executor:
        results = executor.map(get_journals_crossref, files)
    for result in results:
        journal_titles.update(result)
    return list(journal_titles)

async def ask_GPT_about_journal(journal_title, journal_keywords):
    response = await client.chat.completions.create(
        model = "gpt-4-turbo",
        messages = [
            {"role": "system", "content": f"You are given the name of a journal. If the journal is associated with any of the following topics, return 1, else return 0. If unsure, return 2. Your answer must be a single integer. Topics: {journal_keywords}"},
            {"role": "user", "content": f"{journal_title}"}
        ]
    )
    return response.choices[0].message


async def check_journals(journal_titles, journal_keywords, match_whole_word=False, use_AI=False):
    journals_in_field = []
    other_journals = []

    for title in journal_titles:
        matched = False
        for keyword in journal_keywords:
            if match_whole_word:
                if re.search(r'\b' + re.escape(keyword) + r'\b', title, re.IGNORECASE):
                    journals_in_field.append(title)
                    matched = True
                    break
            else:
                if keyword.lower() in title.lower():
                    journals_in_field.append(title)
                    matched = True
                    break
        if not matched:
            other_journals.append(title)

    if use_AI:
        temp_journals_in_field = []
        temp_other_journals = []
        temp_uncertain_journals = []

        if other_journals:  
            tasks = [ask_GPT_about_journal(journal, journal_keywords) for journal in other_journals]
            results = await asyncio.gather(*tasks)

            for journal, result in zip(other_journals, results):
                result = int(result)
                if result == 1:
                    temp_journals_in_field.append(journal)
                elif result == 0:
                    temp_other_journals.append(journal)
                else:
                    temp_uncertain_journals.append(journal)

            return temp_journals_in_field, temp_other_journals, temp_uncertain_journals

    return journals_in_field, other_journals, []

async def main():
    chosen_journals_filepath = "./data/chosen_journals.txt"
    journal_keywords_filepath = "./data/journal_keywords.txt"
    crossref_directory = "./data/crossref/"
    target_journals_filepath = "./data/target_journals.txt"
    excluded_journals_filepath = "./data/excluded_journals.txt"
    uncertain_journals_filepath = "./data/uncertain_journals.txt"

    with open(chosen_journals_filepath, 'r') as file:
        predefined_journals = {line.strip() for line in file}

    with open(journal_keywords_filepath, 'r') as file:
        journal_keywords = [line.strip() for line in file]

    all_journals = get_journals_crossref(crossref_directory)
    
    matched_journals, excluded_journals, uncertain_journals = await check_journals(all_journals, journal_keywords, use_AI=True)
    
    final_journals = set(matched_journals).union(predefined_journals)

    with open(target_journals_filepath, 'w') as file:
        for journal in final_journals:
            file.write(journal + '\n')
    
    with open(excluded_journals_filepath, 'w') as file:
        for journal in excluded_journals:
            file.write(journal + '\n')

    with open(uncertain_journals_filepath, 'w') as file:
        for journal in uncertain_journals:
            file.write(journal + '\n')

if __name__ == '__main__':
    asyncio.run(main())
    
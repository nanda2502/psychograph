from pybliometrics.scopus import AbstractRetrieval
import asyncio
import aiohttp
import urllib
import csv


async def find_doi_by_title(title):
    url = f"https://api.crossref.org/works?query.title={urllib.parse.quote(title)}&rows=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get('message', {}).get('items', [])
                if items:
                    return items[0].get('DOI', False)
            return False


async def process_reference(reference):
    if hasattr(reference, 'doi') and reference.doi:
        return reference.doi
    elif hasattr(reference, 'title') and reference.title:
        try:
            doi = await find_doi_by_title(reference.title)
            return doi
        except:
            return False

    
async def parse_references(references):
    dois = await asyncio.gather(*[process_reference(reference) for reference in references])
    return dois

async def get_edges_from_doi(doi):
    ab = AbstractRetrieval(doi, view='REF')
    references = ab.references if ab.references is not None else []
    ref_dois = await parse_references(references)
    edges = [(doi, ref_doi) for ref_doi in ref_dois if ref_doi]
    return edges

async def get_edges(dois):
    results = await asyncio.gather(*(get_edges_from_doi(doi) for doi in dois))
    flattened_results = [edge for sublist in results for edge in sublist]
    return flattened_results


async def main():
    input_file = './data/dois.txt'
    output_file = './data/edges_scopus.csv'

    with open(input_file, 'r') as file:
        dois = [line.strip() for line in file.readlines()]

    edges = await get_edges(dois)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(edges)

    print(f"Edges have been written to {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
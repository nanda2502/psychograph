import asyncio
import aiohttp
import csv


def read_dois_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]
    
async def get_references_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    async with aiohttp.ClientSession() as session: 
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()  
                    references = data['message'].get('reference', [])
                    return [ref['DOI'] for ref in references if 'DOI' in ref]
                else:
                    print(f"Failed to fetch data: Status code {response.status}")
                    return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

async def get_edges_from_doi(doi):
    references = await get_references_from_doi(doi)
    return [(doi, ref_doi) for ref_doi in references]

async def get_edges(dois):
    results = await asyncio.gather(*(get_edges_from_doi(doi) for doi in dois))
    flattened_results = [edge for sublist in results for edge in sublist]
    return flattened_results

async def main():
    input_file = './data/dois.txt'
    output_file = './data/edges_crossref.csv'
    dois = read_dois_from_file(input_file)
    edges = await get_edges(dois)
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(edges)
    print(f"Edges have been written to {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
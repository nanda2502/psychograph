# Psychograph

Psychograph is a Python project designed to create a citation network of academic articles based on predefined keywords. 

## Prerequisites

Before you can run Psychograph, you need to ensure your system has Python 3.7 or higher installed. This project uses several external libraries which are listed in the `requirements.txt` file.
If you want to run your own search through the crossref database, you will need around 180 GB of disk space to do the search locally. 

## Installation

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/yourgithubusername/psychograph.git
cd psychograph
pip install -r requirements.txt
```

## Usage

Create a ./data directory with the following files

- `keywords.txt`: Contains a list of chosen journals, as well as keywords used for identifying additional journals.
- `crossref/` directory containing the latest crossref public data file. You can download the file from 2023 [here](https://academictorrents.com/details/d9e554f4f0c3047d9f49e448a7004f7aa1701b69)


### Extend Crossref Public Data File to Include 2024 
```bash
python extend_crossref.py
``` 

### Find Journal Articles and Retrieve Metadata
```bash
python doi_retrieval.py
```

After running `doi_retrieval.py`, you will have an edgelist `edges.csv`, and a dictionary with metadata `metadata.pkl`, which includes the publication year, title and subjects of the journal in which the article was published.

### Build Graph

```bash
python graph_psych.py
python annotate_graph.py
``` 


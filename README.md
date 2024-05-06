# Psychograph

Psychograph is an asynchronous Python project designed to create a citation network of academic articles based on predefined keywords and AI-driven content analysis. 

## Prerequisites

Before you can run Psychograph, you need to ensure your system has Python 3.7 or higher installed. This project uses several external libraries which are listed in the `requirements.txt` file.

## Installation

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/yourgithubusername/psychograph.git
cd psychograph
pip install -r requirements.txt
```
## Scopus API Setup
To use the SCOPUS API with pybliometrics you will need to specify an API key. If you have access through an educational institution subscribed to SCOPUS, you can request a key [here](https://dev.elsevier.com/). You will be prompted to enter this key when running the `reference_retrieval_scopus.py` module. Furthermore, SCOPUS can only be used with a connection from an institution with a SCOPUS subscription, this means that you either have to connect directly through your institutional network, configure a proxy in the pybliometrics config file, or use a VPN from your institutional network. 

## Usage

Create a ./data directory with the following files

- `chosen_journals.txt`: Contains a list of predefined journal names that should be included in the search, each on a new line.
- `journal_keywords.txt`: Contains keywords used for identifying additional journal, each on a new line.
- crossref directory containing the latest crossref public data file. You can download the file from 2023  [here](https://academictorrents.com/details/d9e554f4f0c3047d9f49e448a7004f7aa1701b69)


You can run each of the modules separately using the command 
```bash
python -m asyncio <module_name>.py
```

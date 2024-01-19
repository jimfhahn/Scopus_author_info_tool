# load dependencies
from elsapy.elssearch import ElsSearch
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
import pandas as pd
import json
import csv
from datetime import datetime


def main():
    # Load configuration
    with open("config.json") as con_file:
        config = json.load(con_file)

    input_df = pd.read_csv(config['input_file'])

    out_file_name = 'output_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
    error_log_name = initiate_error_log()

    with open(out_file_name, 'w', newline='', encoding='utf-8') as o:
        writer = csv.writer(o)
        writer.writerow(["doi", "original_title", "scp_title", "title_match(true/false)", "creator", "scopus_author_id"])

        for title, year in zip(input_df['title'], input_df['year']):
            ## ensure correct data types
            title = str(title)
            year = int(year)

            doi, creator, scp_title, scopus_author_id = single_doc_processing(title, year, error_log_name, config)

            # check whether title matches
            set1 = set(title.lower().split(" "))
            set2 = set(scp_title.lower().split(" "))
            title_match = (set1 == set2)

            print('article ', title, ': creator ' + creator)
            # write output
            writer.writerow([doi, title, scp_title, title_match, creator, scopus_author_id])


def single_doc_processing(title_str, year, error_log_name, config):
    # Initialize client
    client = ElsClient(config['apikey'])

    # Initialize doc search object and execute search, retrieving all results
    doc_srch = ElsSearch(title_str + ' AND PUBYEAR IS ' + str(year), 'scopus')
    doc_srch.execute(client, get_all = True)

    # Write to dump.json
    with open('dump.json', 'w') as f:
        json.dump(doc_srch.results, f)

    # Load JSON data
    with open('dump.json') as f:
        data = json.load(f)

    # Convert year to string for comparison
    year_str = str(year)

    # Assuming each document in the JSON data has 'dc:title', 'dc:creator', 'prism:coverDate', 'prism:doi', and 'dc:identifier' fields
    for doc in data:
        if doc['dc:title'] == title_str and doc['prism:coverDate'].startswith(year_str):
            # Retrieve the doi, creator, title, and scopus author id
            doi = doc.get('prism:doi', "")
            creator = doc.get('dc:creator', "")
            scp_title = doc.get('dc:title', "")
            scopus_author_id = doc.get('dc:identifier', "")
            return doi, creator, scp_title, scopus_author_id

    print("Document not found in JSON data.")
    error_log_writing("Document not found in JSON data.", error_log_name)
    return "", "", "", ""


def initiate_error_log():
    file_name = 'error_log_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
    with open(file_name, 'w') as file:
        pass
    return file_name


def error_log_writing(message, file_name):
    with open(file_name, 'a') as error_log_file:
        error_log_file.write(message + '\n')


if __name__ == '__main__':
    main()
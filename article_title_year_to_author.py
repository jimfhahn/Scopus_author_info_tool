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

    # out_file_name = 'output_article_title_year_to_author' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
    out_file_name = 'output_article_title_year_to_author' + '.csv'

    error_log_name = initiate_error_log()

    with open(out_file_name, 'w', newline='', encoding='utf-8') as o:
        writer = csv.writer(o)
        writer.writerow(["doi", "article_title", "article_abstract", "article_publication_year", "scopus_author_id", "first_author_name", "num_references", "num_citations", "funder_name", "grant_id"])

        for title, year in zip(input_df['title'], input_df['year']):
            ## ensure correct data types
            title = str(title)
            year = int(year)

            doi, first_author_name, abstract, publication_year, scopus_author_id, num_references, num_citations, funder_name, grant_id = single_doc_processing(title, year, error_log_name, config)

            # write output
            writer.writerow([doi, title, abstract, publication_year, scopus_author_id, first_author_name, num_references, num_citations, funder_name, grant_id])


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

    # Assuming each document in the JSON data has the required fields
    for doc in data:
        if doc['dc:title'] == title_str and doc['prism:coverDate'].startswith(year_str):
            # Retrieve the required fields
            doi = doc.get('prism:doi', "")
            first_author_name = doc.get('dc:creator', "")
            abstract = doc.get('dc:description', "")
            publication_year = doc.get('prism:coverDate', "")[:4]  # Assuming the date is in the format 'YYYY-MM-DD'
            scopus_author_id = doc.get('dc:identifier', "")
            num_references = ""  # This field is not typically included in the JSON data
            num_citations = doc.get('citedby-count', "")
            funder_name = doc.get('prism:fundingAgencies', "")
            grant_id = doc.get('prism:fundingReferences', "")
            return doi, first_author_name, abstract, publication_year, scopus_author_id, num_references, num_citations, funder_name, grant_id

    print("Document not found in JSON data.")
    error_log_writing("Document not found in JSON data.", error_log_name)
    return "", "", "", "", "", "", "", "", ""


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
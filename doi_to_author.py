from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
import pandas as pd
import json
import csv
from datetime import datetime

def parse_author_name(author_name):
    # Split the author's name into family name and given name
    parts = author_name.split(', ')
    if len(parts) == 2:
        return parts[1], parts[0]  # Given name, Family name
    else:
        return '', ''  # Return empty strings if the name cannot be parsed

def main():
    # read input data: a list of papers
    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()

    input_df = pd.read_csv('output_article_title_year_to_author.csv')

    # create output file
    # out_file_name = 'output_doi2author_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
    out_file_name = 'output_doi2author' + '.csv'

    with open(out_file_name, 'w', newline='', encoding='utf-8') as o:
        writer = csv.writer(o)
        writer.writerow(["doi", "author_name", "author_family_name", "author_given_name"])

        # Initialize client
        client = ElsClient(config['apikey'])
        client.inst_token = config['insttoken']

        for doi in input_df['doi']:
            # Initialize doc
            doc = FullDoc(doi = doi)
            if doc.read(client):
                my_authors = doc.data['coredata']['dc:creator']
                print('article ', doi, ': number of authors ' + str(len(my_authors)))
                for author_item in my_authors:
                    author_name = author_item.get('$', '')
                    given_name, family_name = parse_author_name(author_name)
                    writer.writerow([doi, author_name, family_name, given_name])
            else:
                print("Read document failed.")

if __name__ == '__main__':
    main()
# import
from elsapy.elssearch import ElsSearch
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc
import pandas as pd
import json
import csv
from datetime import datetime


def main():
    #print("Please make sure to update the config.json file with your API key, INSTOKEN, and input data file path!")
    #print("input file must have a column named \"ID\""
    #      "(unique ID for each article) and a column named \"doi\" (doi of the article). Please also observe the case!")
    #print("You also need to have elsapy and pandas installed to use this script")

    #user_input = input("Press Y to continue, and press any other key to exit \n")
    #if user_input.lower() != 'y':
    #    exit()

    # read input data: a list of papers
    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()

    input_df = pd.read_csv(config['input_file'])

    # create output file
    out_file_name = 'output_doi_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'

    error_log_name = initiate_error_log()

    with open(out_file_name, 'w', newline='', encoding='utf-8') as o:
        writer = csv.writer(o)
        writer.writerow(
            ["ID", "author_given_name", 'author_surname', 'author_id'])

        for ID, doi in zip(input_df['ID'], input_df['doi']):
            scp_return = single_doc_processing(ID, doi, error_log_name)

            if (scp_return != 'Empty set returned') \
                    and (scp_return != 'Read document failed') \
                    and (scp_return != "No authors field in scp_doc") \
                    and (scp_return != 'Other errors, likely query concatenation error'):
                my_authors = scp_return[0]['author']

                print('article ', str(int(ID)), ': number of authors ' + str(len(my_authors)))
                for author_item in my_authors:
                    writer.writerow([ID,
                                     author_item['preferred-name']['ce:given-name'],
                                     author_item['preferred-name']['ce:surname'],
                                     author_item['@auid']])


def single_doc_processing(ID, doi, error_log_name):
    """
    Function: single_doc_processing
    :param doi: the doi of the article
    :param ID: the id of the article
    :param error_log_name: the path of the error log
    :return: if processed, a dictionary called my authors, and the title retrieved from scopus
    """

    # load configuration
    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()

    # Initialize client
    client = ElsClient(config['apikey'])
    client.inst_token = config['insttoken']

    # construct search string
    # for testing
    try:
        search_str = 'DOI(' + doi + ') '

        doc_srch = ElsSearch(search_str, 'scopus')
        doc_srch.execute(client, get_all=True)

        if doc_srch.hasAllResults():  # retrieve the document
            my_scopus_id = doc_srch.results[0]['dc:identifier'].split(':')[1]
            scp_doc = AbsDoc(scp_id=my_scopus_id)

            if scp_doc.read(client):
                my_authors = scp_doc.data['authors']
                scp_title = scp_doc.title  # save the retrieved title for later checking
                if my_authors:
                    return my_authors, scp_title
                else:
                    print("article  " + str(ID) + " : No authors field in scp_doc")
                    error_log_writing(ID, "No authors field in scp_doc", error_log_name)
                    return "No authors field in scp_doc"
            else:
                print("article  " + str(ID) + " : Read document failed.")
                error_log_writing(ID, "Read document failed.", error_log_name)
                return 'Read document failed'
        else:
            print("article  " + str(ID) + " : Empty set returned")
            error_log_writing(ID, "Empty set returned", error_log_name)
            return 'Empty set returned'
    except:
        print("article  " + str(ID) + ': Other errors, likely query concatenation error')
        error_log_writing(ID, "Empty set returned", error_log_name)
        return 'Other errors, likely query concatenation error'


def initiate_error_log():
    file_name = 'error_log_doi_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
    file = open(file_name, 'w')
    file.close()
    return file_name


def error_log_writing(article_id, message, file_name):
    """
    Function: error_log_writing
    :param article_id: the id of the article that did not get processed
    :param message: message about why this article was not processed
    :param file_name: the file path to the error log
    :return: nothing
    """
    error_log_file = open(file_name, 'a')
    error_log_file.write(str(article_id) + ": " + message + '\n')
    error_log_file.close()


if __name__ == '__main__':
    main()


# load dependencies
from elsapy.elssearch import ElsSearch
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc
import pandas as pd
import json
import csv


def main():

    print("Please make sure to update the config.json file with your API key, INSTOKEN, and input data file path!")
    print("input file must have a column named \"ID\""
          "(unique ID for each article), a column named \"title\"(title of the article), "
          "and a column named \"year\"(publication year of the article). Please also observe the case!")
    print("You also need to have elsapy and pandas installed to use this script")

    user_input = input("Press Y to continue, and press any other key to exit")
    if user_input.lower() != 'y':
        exit()

    # read input data: a list of papers
    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()

    input_df = pd.read_csv(config['input_file'])

    # create output file
    out_file_name = 'output.csv'

    with open(out_file_name, 'w', newline='', encoding='utf-8') as o:
        writer = csv.writer(o)
        writer.writerow(
            ["ID", "original_title", "scp_title", "title_match(true/false)", "author_given_name", 'author_surname',
             'author_id'])

        for ID, title, year in zip(input_df['ID'], input_df['title'], input_df['year']):
            scp_return = single_doc_processing(ID, title, year)

            if (scp_return != 'Empty set returned') \
                    and (scp_return != 'Read document failed') \
                    and (scp_return != "No authors field in scp_doc") \
                    and (scp_return != 'Other errors, likely query concatenation error'):
                my_authors = scp_return[0]['author']

                # check whether title matches
                set1 = set(title.lower().split(" "))
                set2 = set(scp_return[1].lower().split(" "))
                title_match = (set1 == set2)

                print('article ', str(int(ID)), ': number of authors ' + str(len(my_authors)))
                # write output
                for author_item in my_authors:
                    writer.writerow([ID,
                                     title,
                                     scp_return[1],
                                     title_match,
                                     author_item['preferred-name']['ce:given-name'],
                                     author_item['preferred-name']['ce:surname'],
                                     author_item['@auid']])


def single_doc_processing(ID, title_str, year):
    """
    Function: single_doc_processing
    :param ID: the id of the article
    :param title_str: the title
    :param year: the publication year
    :return: if processed, a dictionary called my authors, and the title retrieved from scopus
    """

    # load configuration
    con_file = open("config.json")
    config = json.load(con_file)
    con_file.close()

    # Initialize client
    client = ElsClient(config['apikey'])
    client.inst_token = config['insttoken']

    # try and execpt block: catch unprocessed cases
    try:
        title = '\"' + title_str + '\"'
        search_str = 'TITLE(' + title + ') ' + 'AND PUBYEAR = ' + str(int(year))  # fixing major problem

        doc_srch = ElsSearch(search_str, 'scopus')
        doc_srch.execute(client, get_all=True)

        if doc_srch.hasAllResults():  # retrieve the document
            my_scopus_id = doc_srch.results[0]['dc:identifier'].split(':')[1]
            scp_doc = AbsDoc(scp_id=my_scopus_id)

            if scp_doc.read(client):
                my_authors = scp_doc.data['authors']
                scp_title = scp_doc.title  # save the retrieved title for later double checking
                if my_authors:
                    return my_authors, scp_title
                else:
                    print("No authors field in scp_doc")
                    error_log_writing(ID, "No authors field in scp_doc")
                    return "No authors field in scp_doc"
            else:
                print("Read document failed.")
                error_log_writing(ID, "Read document failed.")
                return 'Read document failed'
        else:
            print("Empty set returned")
            error_log_writing(ID, "Read document failed.")
            return 'Empty set returned'
    except:
        print('Other errors, likely query concatenation error')
        return 'Other errors, likely query concatenation error'


def error_log_writing(article_id, message):
    """
    Function: error_log_writing
    :param article_id: the id of the article that did not get processed
    :param message: message about why this article was not processed
    :return: nothing
    """
    error_log_file = open("error_log.txt", 'a')
    error_log_file.write(str(article_id) + ": " + message + '\n')
    error_log_file.close()


if __name__ == '__main__':
    main()

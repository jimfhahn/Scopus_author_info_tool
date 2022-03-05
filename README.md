# Scopus Author Info Tool

## Project Description
This project tries to streamline author information retrieval from Scopus API for bibliometric data analysis. Currently, by following the step-by-step guide, you can convert a list of articles with title and publication year to their author information, including the given name, surname, and author id. Specifically, by having the author id, you can locate more information about the author from Scopus, such as the author's affiliations. For more information, read the [Scopus data structure description](https://github.com/ElsevierDev/elsapy/wiki/Understanding-the-data).

## Step-by-Step Guide

### Article title&year to author inform (given name, surname and author id)
1. Make sure you have elsapy and Pandas installed in your environment. I used Python 3.8 and 3.9 to develop these scripts, so you should be fine with Python Version >= 3.8. However, I suspect lower version Python 3 still works.  
2. Update the config.json file with your API key, INSTOKEN, and a file path pointing to the input file.  
3. Your input file needs to be in .cvs format. It should contain those three columns with the exact column heads (i.e., case matters): "ID" (unique id for an article), "title" (the title of the article), and "year" (the publication year of the article). We will search the SCOPUS database by the article title and publication year.  
4. Run article_title_year_to_author.py first. It will capture most articles, but there will be a few that cannot be located by a title+year combination. Failed articles will be stored in a file called error_log.txt.  
5. The output file from this step: output_title_year_to_author.csv contains the following columns: "ID" (the id of the article), "original_title" (the title you gave in the input file), "scp_title" (the title of the item retrieved from the query), "title_match(true/false)" (whether the title supplied and the title retrieved match, the false ones needs inspection), "author_given_name" (the given name of the author), "author_surname" (the surname of the author), "author_id" (the Scopus internal id assigned to the author).
6. Inspect rows where "title_match(true/false)" is false. Sometimes, you still retrieved the right article, it is just the title is expressed differently. For example, one common thing I found is that the ':' in a title is converted to '-', causing a failed exact match. On the other hand, you should record the article id of the rows whose original_title and scp_title are apparent mismatch. **Remember to remove those true mismatches before you do Step 11.**
7. What to do with the true mismatch? Those articles needs manual work. You will search their titles in Google Scholar or scopus and find the correct doi for each article. Start an excel sheet and create two columns: "ID" and "doi" (case matters), and record the article ID and doi. When you finish, save the file into a .csv format.
8. You also need to deal with the failed cases (e.g., query returns zero article). Open the error_log.txt. It records the paper ID and the reason for failure. **use the Error message interpretation section below to understand the cause of failures**. You will have to find the DOIs of those articles manually. Continue working with the file you created in Step 7, and write down article id and their dois.
9. Update the config.json file again with the file path pointing to the new input file you created in Step 8. 
10. Run doi_to_author.py. This time, the script will try to locate the article by doi. The output is stored in a new file called "output_doi_to_author.csv." Similar to step 4, you may capture some new articles, but there will still be failures. Failed cases are written into error_log_doi.txt.
11. Combine the information from the **edited** output_title_year_to_author.csv and output_doi_to_author.csv in any way you like. They have different columns. I think the final dataset should have ID, title, author_given_name, author_surname, and author_id. But it is up to you.
12. You have to manually identify the author information for those articles in error_log_doi.txt, and fill the author information into the file generated in Step 11.

## Code Description
article_title_year_to_author.py: convert article information (title and publication year) to an author list with author given name, author surname, and author id. Developed using [elsapy Python module](https://github.com/ElsevierDev/elsapy).

doi_to_author.py: convert article information (doi) to author lists with author given name, author surname, and author id. Developed using [elsapy Python module](https://github.com/ElsevierDev/elsapy).

## Error message interpretation
No authors field in scp_doc: This document can be found in Scopus. However, the record of the document lacks author fields.
Read document failed: This document can be found in Scopus. However, for some technical reason, the record cannot be read.
Empty set returned: No record was retrieved. Either the document was not indexed in Scopus.
Other errors, likely query concatenation error: The search call failed. Check whether your query string was concatenated correctly. 

## Contact
Author: Yuanxi Fu (@yuanxiesa)  
Submit issues if you have any question or comment about the code.

## Version History

### version 1.0.1 (2022-03-02)
- added date-time string to error-log.txt and output.txt so new files will not overwrite old files.
- fixed error message misprint.

### version 1.0.0 (2022-01-22)
- initial release.


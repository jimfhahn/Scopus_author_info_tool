# Scopus Author Info Collection

## Project Description
This project tries to streamline the process of pulling author information from Scopus API. 
## Step-by-Step Guide
1. Make sure you have ElsAPY and Pandas installed in your environment. I used Python 3.8 and 3.9 to develop these scripts.
2. Update the config.json file with your API key, INSTOKEN, and a file path pointing to the input file.
3. Your input file needs to be in .cvs format. It should contain those three columns with the exact column heads (i.e., case matters): "ID" (unique id for an article), "title" (the title of the article), and "year" (the publication year of the article).
4. Run article_title_year_to_author.py first. It will capture most articles (stored in the output.csv), but there will be a few that cannot be located by a title+year combination. Failed articles will be stored in a file called error_log.txt
5. Open the error_log.txt. It records the paper ID and the reason for failure. You will have to find the DOIs of those articles manually. Save your findings in another .csv file, with two columns (again, case matters): "ID" (the id of the article) and 'doi' (the doi of the article).
6. Update the config.json file again with the file path pointing to the new input file you created in step 5. 
7. Run doi_to_author.py. This time, the script will try to locate the article by doi, which is a more precise way to find an article. The output is stored in a new file called "output_doi.csv." Similar to step 4, you may capture some new articles, but there will still be failures. Failed cases are written into error_log_doi.txt.
8. Concactnate output.csv and output_doi.csv to one file.
9. You have to manually identify the author information for those articles in error_log_doi.txt, and fill the author information into the file generated in Step 8.

## Code Description

### Overview
This project extracted the TEXT and MTEXT information from dwg files. The cleaned data was loaded to an Elasticsearch instance.
Sample DWG files were provided in the /dwg folder, which was obtained from:
https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/6XGQklp3ZcBFqljLPjrnQ9.html
https://q-cad.com/samples/autocad-2d-samples/

See Also: https://github.com/sfyuen/dwg-full-text-search

### Prerequisites
1.	Python
2.	Elasticsearch 7

### Instructions
1.	Install python packages from requirements.txt
2.	Edit main.py:
    * directory: local directory of the dwg files
    * esindex: Index name of Elasticsearch to add the documents
    * escredential: Credentials of Elasticsearch, requires writing privilege
    * "path" variable of function "load": URL path to download each of your DWG files
3.	Execute main.py:

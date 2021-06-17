# HEE Search Bank Migration
This project will be used to migrate the existing HEE search banks onto brXM (Bloomreach Experience Manager) platform.

The project essentially extracts search bank data from the given JSON file and builds YAML files for search banks along with its associated value-lists which can readily be imported to brXM.

## Pre Requisites
In order to develop and run on this platform you will need to have the `Docker` installed.

## Run with Docker Compose
Execute the following command to run the script:

```
>> docker-compose up --build
```

Make sure to update the following volumes and environment variables before running the script:

- Volumes
  - /input: The volume under which the search bank JSON data file should be placed.
  - /output: The volume under which the outputs will be stored. The migration script produces the following outputs:
    - `brxm-search-bank-providers.zip`: An export of search bank providers which could readily be imported onto brXM as `/content/documents/administration/valuelists/kls/searchbankproviders` value-list.
    - `brxm-search-bank-topics.zip`: An export of search bank topics which could readily be imported onto brXM as `/content/documents/administration/valuelists/kls/searchbanktopics` value-list.
    - `brxm-search-banks.zip`: An export of search banks with associated (strategy & search) documents which could readily be imported onto brXM as `hee:searchBank` documents under `Migrated Search Banks` folder.
- Environment Variables
  - INPUT_SEARCH_BANK_JSON_FILE_PATH: Input search banks JSON file path. Refer `HEE-271` for the format of the JSON.
  - OUTPUT_DIRECTORY: The output directory wherein the output archives will be stored. Note that the path must end with a trailig slash.
  - DEBUG: A (python) Boolean [True/False] indicating whether DEBUG is enabled or not.

## Importing outputs onto brXM
- Login to the brXM console (`/cms/console`) of the environment wherein search banks along with its associated value-lists needs to be imported (with `xm.console.user` privilege).
- Import `brxm-search-bank-providers.zip` under `/content/documents/administration/valuelists/kls` node in order to import the search bank providers.
- Import `brxm-search-bank-topics.zip` under `/content/documents/administration/valuelists/kls` node in order to import the search bank topics.
- Import `brxm-search-banks.zip` under `/content/documents/lks` node in order to import search banks under `Migrated Search Banks` folder.
- Login to brXM CMS (`/cms`) of the environment wherein the search banks have been imported (with privilege to edit documents of `hee:searchBank` type) and publish them all by choosing `Publish all in folder...` on `Migrated Search Banks` folder.

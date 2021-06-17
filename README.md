# HEE Search Bank Migration
This project will be used to migrate the existing HEE search banks onto brXM (Bloomreach Experience Manager) platform (in chunks).

The project essentially extracts search bank data from the given JSON file and builds YAML files in chunks for search banks along with its associated value-lists which can readily be imported to brXM.

Note that the max upload limit of CMS (Console imports) seem to have been `10MB` for brCloud [https://documentation.bloomreach.com/12/bloomreach-cloud/reference-documentation/restrictions-and-limitations.html](Bloomreach Cloud Restrictions and Limitations) and so importing files which are larger than `10MB` will end up with `413 Request Entity Too Large` error. In order to workaround this issue, the migration script builds YAML files (along with its associated strategy & search documents) in chunks (as indicated by `OUTPUT_SEARCH_BANK_CHUNK_SIZE` environment variable).

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
    - `brxm-search-banks-{n}.zip`: An export of search bank chunks (whose size can be configured via `OUTPUT_SEARCH_BANK_CHUNK_SIZE` environment variable) with associated (strategy & search) documents which could readily be imported onto brXM as `hee:searchBank` documents.
- Environment Variables
  - INPUT_SEARCH_BANK_JSON_FILE_PATH: Input search banks JSON file path. Refer `HEE-271` for the format of the JSON.
  - OUTPUT_SEARCH_BANK_CHUNK_SIZE: The output chunk size of search bank YAML files i.e. the size of search bank documents which would be exported as YAML files.
  - OUTPUT_DIRECTORY: The output directory wherein the output archives will be stored. Note that the path must end with a trailig slash.
  - DEBUG: A (python) Boolean [True/False] indicating whether DEBUG is enabled or not.

## Importing outputs onto brXM
- Login to the brXM CMS console (`/cms/console`) of the environment wherein search banks along with its associated value-lists needs to be imported (with `xm.console.user` privilege).
- Import `brxm-search-bank-providers.zip` under `/content/documents/administration/valuelists/kls` node in order to import the search bank providers.
- Import `brxm-search-bank-topics.zip` under `/content/documents/administration/valuelists/kls` node in order to import the search bank topics.
- Now, login to brXM CMS (`/cms`) of the environment wherein the search banks needs to be imported (with privilege to edit documents of folders) and create `Migrated Search Banks` folder under `KLS` root folder with `new-searchBank-folder` and `new-searchBank-document` allowed template queries.
- Switch back to brXM CMS console (`/cms/console`) and import `brxm-search-banks-{n}.zip` files under `/content/documents/lks/migrated-search-banks` node (one by one) in order to import search bank chunks under `Migrated Search Banks` folder.
- switch back to brXM CMS (`/cms`) (with admin privilege) and navigate to `MoveChunkedSearchBankHandlesUnderMigratedSearchBanksGrandParentFolder` updater script and execute in order to move all chunked Search Bank documents under `Migrated Search Banks` grand parent folder.
- Switch back to brXM CMS console (`/cms/console`) and delete the empty chunk folders `migrated-search-bank-{n}` available under `/content/documents/lks/migrated-search-banks` node.
- Switch back to brXM CMS (`/cms`) (with privilege to publish documents of `hee:searchBank` type) and publish them all by choosing `Publish all in folder...` on `Migrated Search Banks` folder.

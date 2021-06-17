import json
import os
import shutil
from zipfile import ZipFile

from ruamel.yaml import YAML

import search_bank_brxm_yaml_decorator as search_bank_decorator
import search_bank_extractor as extractor
import search_bank_value_list_brxm_yaml_decorator as search_bank_value_list_decorator

# OUTPUTS
OUTPUT_BRXM_SEARCH_BANK_PROVIDERS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-search-bank-providers'
OUTPUT_BRXM_SEARCH_BANK_TOPICS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-search-bank-topics'
OUTPUT_BRXM_SEARCH_BANKS_YAML_FILE_NAME_WITHOUT_EXTN = 'brxm-search-banks'
OUTPUT_UNPROCESSED_SEARCH_BANKS_JSON_FILE_PATH = 'unprocessed-search-banks.json'


def archive_brxm_yaml_file(yaml_file_path, archive_file_path):
    with ZipFile(archive_file_path, 'w') as zipObj:
        zipObj.write(yaml_file_path, os.path.basename(yaml_file_path))

def archive_brxm_files(yaml_file_path, output_directory, documents_directory, archive_file_path):
    with ZipFile(archive_file_path, 'w') as zipObj:
        zipObj.write(yaml_file_path, os.path.basename(yaml_file_path))
        for folderName, subfolders, filenames in os.walk(documents_directory):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath, filePath.replace(output_directory, ''))

def dump_brxm_yaml_file(decorated_yaml_object, yaml_file_path):
    yaml = YAML()
    yaml.indent(offset = 2)
    yaml.representer.ignore_aliases = lambda *data: True

    with open(yaml_file_path, 'w') as file:
        yaml.dump(decorated_yaml_object, file)

def dump_unprocessed_search_banks(unprocessed_search_banks, output_json_file_path):
    with open(output_json_file_path, 'w') as file:
        file.write(json.dumps(unprocessed_search_banks))

def delete_directory_content(directory_path):
    # Gather directory contents
    dir_contents = [os.path.join(directory_path, f) for f in os.listdir(directory_path)]

    # Iterate and remove each item in the appropriate manner
    [os.remove(f) if os.path.isfile(f) or os.path.islink(f) else shutil.rmtree(f) for f in dir_contents]

def dump_yaml_and_archive(object_plural_name, decorated_object, output_yaml_file_path_without_extn):
    # Dump decorated object as yaml file
    output_yaml_file_path = f'{output_yaml_file_path_without_extn}.yaml'
    output_archive_yaml_file_path = f'{output_yaml_file_path_without_extn}.zip'
    dump_brxm_yaml_file(decorated_object, output_yaml_file_path)
    print(f'brXM migrated search bank {object_plural_name} yaml file {output_yaml_file_path} has successfully been generated\n')

    # Archive yaml file
    archive_brxm_yaml_file(output_yaml_file_path, output_archive_yaml_file_path)
    print(f'brXM migrated search bank {object_plural_name} yaml file {output_yaml_file_path} has successfully been archived as {output_archive_yaml_file_path}\n')

def main():
    # ENVIRONMENT VARIABLES
    INPUT_SEARCH_BANK_JSON_FILE_PATH = os.getenv('INPUT_SEARCH_BANK_JSON_FILE_PATH')
    OUTPUT_SEARCH_BANK_CHUNK_SIZE = int(os.getenv('OUTPUT_SEARCH_BANK_CHUNK_SIZE'))
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY')
    DEBUG = eval(os.getenv('DEBUG'))

    search_banks, unprocessed_search_banks, provider_dict, topic_dict  = extractor.extract_search_bank_with_value_lists(INPUT_SEARCH_BANK_JSON_FILE_PATH, DEBUG)

    if DEBUG:
        print(f'\nExtracted & Formatted Provider = {provider_dict}\n')
        print(f'\nUnprocessed (raw) Search Banks (due to failure in parsing data) = {unprocessed_search_banks}\n')
        print(f'\nExtracted & Formatted Topics = {topic_dict}\n')
        print(f'\nExtracted Search Banks = {search_banks}\n')

    # Cleanup existing/old output directory content
    delete_directory_content(OUTPUT_DIRECTORY)

    # PROVIDERS
    # Decorate providers for brXM import
    decorated_providers = search_bank_value_list_decorator.get_decorated_value_list_handle(provider_dict, 'searchbankproviders', 'SearchBankProviders')
    if DEBUG:
        print(f'Decorated Providers = {decorated_providers}\n')

    dump_yaml_and_archive(
        'providers',
        decorated_providers,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_SEARCH_BANK_PROVIDERS_YAML_FILE_NAME_WITHOUT_EXTN}')


    # TOPICS
    # Decorate topics for brXM import
    decorated_topics = search_bank_value_list_decorator.get_decorated_value_list_handle(topic_dict, 'searchbanktopics', 'SearchBankTopics')
    if DEBUG:
        print(f'Decorated Topics = {decorated_topics}\n')

    dump_yaml_and_archive(
        'topics',
        decorated_topics,
        f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_SEARCH_BANK_TOPICS_YAML_FILE_NAME_WITHOUT_EXTN}')


    # SEARCH BANKS
    # Decorate migrated search banks for brXM import
    # NOTE that it also downloads the associated search bank strategy and search documents
    # along with text extracted from PDF files as a binary resource
    chunked_search_banks = [search_banks[i:i + OUTPUT_SEARCH_BANK_CHUNK_SIZE] for i in range(0, len(search_banks), OUTPUT_SEARCH_BANK_CHUNK_SIZE)]

    chunk_counter = 0
    for search_bank_chunk in chunked_search_banks:
        chunk_counter += 1
        decorated_search_bank_chunk = search_bank_decorator.get_decorated_migrated_search_bank_chunk_folder(search_bank_chunk, OUTPUT_DIRECTORY, chunk_counter)

        if DEBUG:
            print(f'Decorated Search Bank Chunk = {decorated_search_bank_chunk}\n')

        # Dump decorated migrated search banks as yaml file
        output_search_banks_file_path = f'{OUTPUT_DIRECTORY}{OUTPUT_BRXM_SEARCH_BANKS_YAML_FILE_NAME_WITHOUT_EXTN}-{chunk_counter}'
        output_search_banks_yaml_file_path = f'{output_search_banks_file_path}.yaml'
        output_search_banks_archive_yaml_file_path = f'{output_search_banks_file_path}.zip'
        output_search_banks_documents_file_path = f'{OUTPUT_DIRECTORY}documents-{chunk_counter}'
        dump_brxm_yaml_file(decorated_search_bank_chunk, output_search_banks_yaml_file_path)
        print(f'brXM migrated search bank chunk yaml file {output_search_banks_yaml_file_path} has successfully been generated\n')

        # Archive search banks yaml file and its associated [strategy & search] documents
        archive_brxm_files(
            output_search_banks_yaml_file_path,
            OUTPUT_DIRECTORY,
            output_search_banks_documents_file_path,
            output_search_banks_archive_yaml_file_path)
        print(f'Both brXM migrated search bank chunk yaml file {output_search_banks_yaml_file_path} and its associated [strategy & search] documents (available under {output_search_banks_documents_file_path}) has successfully been archived as {output_search_banks_archive_yaml_file_path}\n')

    if unprocessed_search_banks:
        output_unprocessed_search_banks_file_path = f'{OUTPUT_DIRECTORY}{OUTPUT_UNPROCESSED_SEARCH_BANKS_JSON_FILE_PATH}'
        dump_unprocessed_search_banks(unprocessed_search_banks, output_unprocessed_search_banks_file_path)

        print(f'Unprocessed (raw) Search Banks {unprocessed_search_banks} have successfully been dumped onto {output_unprocessed_search_banks_file_path}\n')

if __name__ == '__main__':
    main()

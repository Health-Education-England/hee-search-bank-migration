import mimetypes
import os
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
import tika
from tika import parser
from unidecode import unidecode


def get_current_utc():
    return datetime.now(timezone.utc)

def get_brxm_node_name(title, length):

    normalised_title = unicodedata.normalize('NFKD', title.strip()).encode('ascii', 'ignore').decode()
    non_alpha_numeric_chars_stripped_title = re.sub(r'[^A-Za-z0-9 -]+', '', normalised_title)
    return non_alpha_numeric_chars_stripped_title[:length].lower().replace(' ', '-')

def get_decorated_document_handle_object(title):
    return {
        'jcr:primaryType': 'hippo:handle',
        'jcr:mixinTypes': ['hippo:named', 'hippo:versionInfo', 'mix:referenceable'],
        'hippo:name': f'{title}'
    }

def get_filename(document_url):
    filename = document_url[document_url.rfind("/") + 1:]

    # Replaces whitespaces with underscores
    filename = re.sub(r'\s+', '_', filename)

    return filename

def get_mime_type(filename):
    return mimetypes.types_map[os.path.splitext(filename)[1]]

def generate_text_version_of_pdf(pdf_file_path, output_file_path):
    with open(output_file_path, 'w') as f:
        f.write(parser.from_file(pdf_file_path)['content'])

def make_file_path_directory(file_path):
    # Makes file directory if not already exists
    file_directory = Path(os.path.dirname(file_path))
    file_directory.mkdir(parents = True, exist_ok = True)

def download_document(document_url, output_file_path):
    make_file_path_directory(output_file_path)

    r = requests.get(document_url.replace(' ', '%20'), allow_redirects = True)

    with open(output_file_path, 'wb') as f:
        f.write(r.content)

def create_default_hippo_resource(output_file_path):
    make_file_path_directory(output_file_path)

    os.system(f'touch {output_file_path}')

def get_document_node(search_bank_node_name, document_url, output_directory):
    if document_url:
        filename = get_filename(document_url)
        relative_output_file_path = f'documents/{search_bank_node_name}/{filename}'
        download_document(document_url, f'{output_directory}{relative_output_file_path}')
        mime_type = get_mime_type(filename)
    else:
        filename = 'hippo:resource'
        relative_output_file_path = f'documents/{search_bank_node_name}/hippo-resource'
        create_default_hippo_resource(f'{output_directory}{relative_output_file_path}')
        mime_type = 'application/vnd.hippo.blank'

    document_node = {
        'jcr:primaryType': 'hippo:resource',
        'hippo:filename': filename,
        'jcr:encoding': 'UTF-8',
        'jcr:lastModified': get_current_utc(),
        'jcr:mimeType': mime_type,
        'jcr:data': {
            'type': 'binary',
            'resource': relative_output_file_path
        }
    }

    if mime_type == 'application/pdf':
        splitted_file_name = os.path.splitext(filename)
        relative_output_text_file_path = f'documents/{search_bank_node_name}/{splitted_file_name[0]}_text{splitted_file_name[1]}'

        generate_text_version_of_pdf(f'{output_directory}{relative_output_file_path}', f'{output_directory}{relative_output_text_file_path}')

        document_node['hippo:text'] = {
            'type': 'binary',
            'resource': relative_output_text_file_path
        }

    return document_node

def get_decorated_migrated_search_bank_folder_object():
    return {
        "jcr:primaryType": "hippostd:folder",
        "jcr:mixinTypes": ["hippo:named", "hippotranslation:translated", "mix:versionable"],
        "hippo:name": "Migrated Search Banks",
        "hippostd:foldertype": ["new-searchBank-folder", "new-searchBank-document"],
        "hippotranslation:id": str(uuid.uuid4()),
        "hippotranslation:locale": "en"
    }

def get_decorated_search_bank_object(search_bank, search_bank_node_name, state, availability, translation_uuid, output_directory):
    decorated_search_bank = {}

    # Add meta data
    decorated_search_bank['jcr:primaryType'] = 'hee:searchBank'
    decorated_search_bank['jcr:mixinTypes'] = ['mix:referenceable', 'mix:versionable']
    decorated_search_bank['hippo:availability'] = availability
    decorated_search_bank['hippostd:retainable'] = False
    decorated_search_bank['hippostd:state'] = state
    decorated_search_bank['hippostdpubwf:createdBy'] = 'admin'
    decorated_search_bank['hippostdpubwf:lastModifiedBy'] = 'admin'
    decorated_search_bank['hippostdpubwf:creationDate'] = get_current_utc()
    decorated_search_bank['hippostdpubwf:lastModificationDate'] = get_current_utc()
    decorated_search_bank['hippotranslation:id'] = translation_uuid
    decorated_search_bank['hippotranslation:locale'] = 'en'

    # Add SearchBank data
    decorated_search_bank['hee:title'] = f'{unidecode(search_bank["title"])}'
    decorated_search_bank['hee:topics'] = search_bank["topics"]
    decorated_search_bank['hee:keyTerms'] = ''
    decorated_search_bank['hee:provider'] = f'{search_bank["provider"]}'
    decorated_search_bank['hee:completedDate'] = datetime.strptime(search_bank["completed_date"], '%d/%m/%Y')

    decorated_search_bank['/hee:strategyDocument'] = get_document_node(search_bank_node_name, search_bank['strategy_doc_url'], output_directory)
    decorated_search_bank['/hee:searchDocument'] = get_document_node(search_bank_node_name, search_bank['search_doc_url'], output_directory)

    return decorated_search_bank

def get_decorated_migrated_search_banks_folder(search_banks, output_directory):
    # Initialising mimetypes and tika modules
    mimetypes.init()
    tika.initVM()

    decorated_migrated_search_bank_folder = {}
    search_bank_node_names = []

    # Build migrated-search-bank folder node
    decorated_migrated_search_bank_folder['/migrated-search-bank'] = get_decorated_migrated_search_bank_folder_object()

    for search_bank in search_banks:
        print(f'Decorating Search Bank with title = {search_bank["title"]}')

        search_bank_node_name = get_brxm_node_name(search_bank['title'], 50)
        temp_search_bank_node_name = search_bank_node_name

        loop_counter = 0
        while temp_search_bank_node_name in search_bank_node_names:
            loop_counter += 1
            temp_search_bank_node_name = f'{search_bank_node_name}_{loop_counter}'

        search_bank_node_name = temp_search_bank_node_name

        search_bank_node_names.append(search_bank_node_name)

        # Build hee:searchBank handle node
        decorated_migrated_search_bank_folder['/migrated-search-bank']['/' + search_bank_node_name] = get_decorated_document_handle_object(search_bank['title'])

        translation_uuid = str(uuid.uuid4())

        # Build hee:searchBank node for draft version
        decorated_migrated_search_bank_folder['/migrated-search-bank']['/' + search_bank_node_name]['/' + search_bank_node_name + '[1]'] = get_decorated_search_bank_object(search_bank, search_bank_node_name, 'draft', [], translation_uuid, output_directory)

        # Build hee:searchBank node for unpublished version
        decorated_migrated_search_bank_folder['/migrated-search-bank']['/' + search_bank_node_name]['/' + search_bank_node_name + '[2]'] = get_decorated_search_bank_object(search_bank, search_bank_node_name, 'unpublished', ['preview'], translation_uuid, output_directory)

    return decorated_migrated_search_bank_folder

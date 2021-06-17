import json
import re
import traceback

from sortedcontainers import SortedDict


def get_strategy_doc_url(strategy_anchor_tag):
    if strategy_anchor_tag:
        pattern = re.compile('<a href=\"(.*?)\"(.*)')
        matches = pattern.search(strategy_anchor_tag)

        if matches:
            return matches.group(1)
        else:
            raise Exception(f'No match found for Strategy Document URL in the given data {strategy_anchor_tag}')
    else:
        return ''

def get_completed_date_search_doc_url_and_provider(completd_data):
    pattern = re.compile('^\d{3}\s*-\s*(.*?)\s*\n{1,2}(<a href="(.*?)"(.*?)</a>\]?\n{0,2})?(?!<a href=)((.*?)\.?\s?\n{0,2}?)?$')
    matches = pattern.search(completd_data)

    if matches:
        return matches.group(1), matches.group(3), matches.group(6)
    else:
        raise Exception(f'No match found for Completed Date, Search Document URL and Provider in the given data {completd_data}')

def get_dict(s):
    d = {}

    # Uses underscore formatted element and element as the key and the value
    for e in s:
        if e:
            d.update({re.sub(r'\s+', '_', re.sub(r'[^A-Za-z0-9 _-]+', '', e)).lower():e})

    return SortedDict(d)

def redecorate_search_banks(search_banks, provider_dict, topic_dict):
    for search_bank in search_banks:
        provider = [k for k, v in provider_dict.items() if v in search_bank['provider']]
        if provider:
            search_bank['provider'] = provider[0]

        search_bank['topics'] = [k for k, v in topic_dict.items() if v in search_bank['topics']]

def extract_search_bank_with_value_lists(search_bank_json_data_file_path, debug):
    search_banks = []
    unprocessed_search_banks = []
    topics, providers = (set() for i in range(2))

    with open(search_bank_json_data_file_path) as f:
        search_bank_json = json.load(f)

        if debug:
            print(f'Raw Extracted Search Bank Data = {search_bank_json["data"]}')

        # Loop starting from the second element of the array
        # as the first one contains field/column names
        for search_bank in search_bank_json['data'][1:]:
            try:
                search_bank_topics = [topic.strip() for topic in search_bank[0].split(',')]
                completed_date, search_doc_url, provider = get_completed_date_search_doc_url_and_provider(search_bank[4])

                providers.add(provider)
                topics.update(set(search_bank_topics))

                search_banks.append({
                    'title': search_bank[1],
                    'topics': search_bank_topics,
                    # 'keyTerms': '',
                    'strategy_doc_url': get_strategy_doc_url(search_bank[2]),
                    'completed_date': completed_date,
                    'search_doc_url': search_doc_url,
                    'provider': provider,
                })
            except:
                print(traceback.format_exc())
                print(f'Caught error while processing the SearchBank data {search_bank}. Try adding this to CMS manually!')
                unprocessed_search_banks.append(search_bank)

        # Convert set of providers and topics to dictionaries with underscore decorated value as key
        provider_dict = get_dict(providers)
        topic_dict = get_dict(topics)

        # Redecorates search banks with providers and topics keys
        redecorate_search_banks(search_banks, provider_dict, topic_dict)

    return search_banks, unprocessed_search_banks, provider_dict, topic_dict

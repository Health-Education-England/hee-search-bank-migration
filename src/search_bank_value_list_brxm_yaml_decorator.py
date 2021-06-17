import uuid


def get_decorated_value_list_handle_object(label):
    return {
        'jcr:primaryType': 'hippo:handle',
        'jcr:mixinTypes': ['hippo:named', 'mix:referenceable'],
        'hippo:name': label
    }

def get_decorated_value_list_handle(d, name, label):
    decorated_value_list_handle = {}

    # Build selection:valuelist handle node
    decorated_value_list_handle[f'/{name}'] = get_decorated_value_list_handle_object(label)

    decorated_value_list = {}
    decorated_value_list['jcr:primaryType'] = 'selection:valuelist'
    decorated_value_list['jcr:mixinTypes'] = ['hippotranslation:translated', 'mix:referenceable']
    decorated_value_list['hippo:availability'] = ['live', 'preview']
    decorated_value_list['hippotranslation:id'] = str(uuid.uuid4())
    decorated_value_list['hippotranslation:locale'] = 'inherited - from query'

    # Builds selection:valuelist nodes
    for count, (k, v) in enumerate(d.items(), start = 1):
        decorated_value_list['/selection:listitem[' + str(count) + ']'] = {
            'jcr:primaryType': 'selection:listitem',
            'selection:key': k,
            'selection:label': v
        }

    decorated_value_list_handle[f'/{name}'][f'/{name}'] = decorated_value_list

    return decorated_value_list_handle
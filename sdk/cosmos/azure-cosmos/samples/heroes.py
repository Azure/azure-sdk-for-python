import uuid

def get_generic_hero():
    hero_item = {
    'id': 'Generic_Hero_' + str(uuid.uuid4()),
    'lastName': 'Smith',
    'parents': None,
    'children': None,
    'address': {
        'state': 'FL',
        'city': 'Miami'
    },
    'saved': ['block'], 
    'professional': False,
    'company': None
    }
    return hero_item

def get_batman():
    hero_item = {
    'id': 'Batman',
    'lastName': 'Wayne',
    'parents': None,
    'children': None,
    'address': {
        'state': 'WA',
        'city': 'Gotham'
    },
    'saved': ['state', 'city'], 
    'professional': True,
    'company': 'DC'
    }
    return hero_item

def get_flash():
    hero_item = {
    'id': 'Flash',
    'lastName': 'Allen',
    'parents': None,
    'children': None,
    'address': {
        'state': 'NY',
        'city': 'New York'
    },
    'saved': ['world','country'], 
    'professional': True,
    'company': 'DC'
    }
    return hero_item

def get_superman():
    hero_item = {
    'id': 'Superman',
    'lastName': 'Kent',
    'parents': None,
    'children': None,
    'address': {
        'state': 'WA',
        'city': 'Metropolis'
    },
    'saved': ['universe','world','country', 'state'], 
    'professional': True,
    'company': 'DC'
    }
    return hero_item

def get_spider():
    hero_item = {
    'id': 'Spiderman',
    'lastName': 'Parker',
    'parents': None,
    'children': None,
    'address': {
        'state': 'NY',
        'city': 'New York'
    },
    'saved': ['galaxy','world','country'], 
    'professional': True,
    'company': 'Marvel'
    }
    return hero_item

def get_iron():
    hero_item = {
    'id': 'Ironman',
    'lastName': 'Stark',
    'parents': None,
    'children': None,
    'address': {
        'state': 'NY',
        'city': 'New York'
    },
    'saved': ['galaxy','world','country'], 
    'professional': True,
    'company': 'Marvel'
    }
    return hero_item
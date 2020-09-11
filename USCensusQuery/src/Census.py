import json
import urllib2
from itertools import izip


class Census:
    def __init__(self, key):
        self.key = key

    '''
    Retrieves demographics from Census API for a given year, organizes
    the response into a dictionary keyed by label, and returns
    them in a nested dictionary keyed by tract.
    Params:
        code_dict: a dictionary relating demographic labels and their Census codes
        geo: a list representing the geography hierarchy
        year: the year of the data
        dataset: dataset from which to retrieve data (e.g. acs1, acs5, pep)
    Returns:
        A nested dictionary in the form:
        {tract:
            {label:
            }
        }
    NOTE: borrows from https://stackoverflow.com/questions/28933220/us-census-api-get-the-population-of-every-city-in-a-state-using-python
    '''

    def get(self, code_dict, state_code, county_code, year, dataset, bg=False):
        codes, labels = code_dict.keys(), code_dict.values()
        fields = [','.join(codes)]
        base_url = 'https://api.census.gov/data/%s/%s?key=%s&get=' % (str(year), dataset, self.key)
        query = fields
        level = 'block%20group' if bg else 'tract'
        geo = ['for={}:*'.format(level), 'in=state:{}%20county:{}'.format(state_code, county_code)]
        for item in geo:
            query.append(item)
        add_url = '&'.join(query)
        url = base_url + add_url
        response = ''
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print 'Census API call failed because: '
            print e.reason
            print e.read()
            print 'Exiting...'
            exit(1)
        json_resp = json.load(response)

        iterjson = iter(json_resp)
        next(iterjson)
        year_dict = {}
        for tract_data in iterjson:
            if bg:
                tract = '{}.{}'.format(tract_data[-2].encode('utf8'), tract_data[-1].encode('utf8'))
            else:
                tract = tract_data[-1].encode('utf8')
            year_dict[tract] = {}
            for label, value in izip(labels, tract_data[:-3]):
                year_dict[tract][label] = int(value) if (value is not None and int(value) >= 0) else None

        return year_dict

    '''
    Returns a dictionary of all states (values) and their Census codes (keys).
    '''

    def get_state_dict(self, year, dataset):
        url = 'https://api.census.gov/data/{}/{}?get=NAME&for=state:*&key={}'.format(year, dataset, self.key)
        response = urllib2.urlopen(url)
        data = json.load(response)
        d = {}
        for item in data:
            if item[0].encode('utf8') != "NAME":
                try:
                    d[item[1].encode('utf8')] = item[0].encode('utf8')
                except UnicodeDecodeError as e:
                    print e
                    print item
                    exit(1)
        return d

    '''
    Returns a dictionary of all counties (values) and their Census codes (keys).
    '''

    def get_county_dict(self, state_code):
        url = 'https://api.census.gov/data/2013/acs5?get=NAME&for=county:*&in=state:{}&key={}'.format(state_code,
                                                                                                      self.key)
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print 'Census API call failed because: '
            print e.reason
            print e.read()
            print 'Exiting...'
            exit(1)

        data = json.load(response)
        d = {}
        for item in data:
            if item[-1].encode('utf8') != 'county':
                try:
                    d[item[-1].encode('utf8')] = item[0].split(',')[0].encode('utf8')
                except UnicodeDecodeError as e:
                    print e
                    print item
                    exit(1)
        return d

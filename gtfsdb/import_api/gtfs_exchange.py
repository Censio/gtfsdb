__author__ = 'rhunter'
from gtfsdb.import_api.common import get_url

def recent_file(datafiles):
    if datafiles and len(datafiles) > 0:
        return max(datafiles, key = lambda k: k['date_added'])


def get_gtfs_agencies():
    return get_url('http://www.gtfs-data-exchange.com/api/agencies')


def get_gtfs_agency_details(agency):
    return get_url('http://www.gtfs-data-exchange.com/api/agency?agency={}'.format(agency['dataexchange_id']))

def get_most_recent_file(agency):
    full_details = get_gtfs_agency_details(agency)
    return { 'name': agency['name'], 'file': recent_file(full_details['datafiles'])}



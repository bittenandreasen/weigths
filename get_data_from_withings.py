import configparser
import datetime
import urllib
from urllib.request import urlopen

import simplejson

WITHINGS_URL = "http://wbsapi.withings.net/measure?action=getmeas&userid={user_id}&publickey={user_public_key}"


def get_user_configuration():
    config = configparser.ConfigParser()
    config.read(['config_local.cfg'])
    users = config.get('WITHINGS', 'users').split(',')
    user_ids = config.get('WITHINGS', 'user_ids').split(',')
    user_public_keys = config.get('WITHINGS', 'user_public_keys').split(',')
    users = zip(users, user_ids, user_public_keys)
    return users


def get_data_from_withings():
    data_from_withings = {}
    users = get_user_configuration()
    for (user, user_id, user_public_key) in users:
        data_from_withings[user] = {}
        url_to_get_info_from_withings = WITHINGS_URL.format(
            user_id=user_id,
            user_public_key=user_public_key
        )
        data = simplejson.loads(urlopen(url_to_get_info_from_withings).read())
        for measure in data['body']['measuregrps']:
            if measure['category'] == 1:
                for m in measure['measures']:
                    if m['type'] == 1:
                        scale = 10.0 ** (-m['unit'])
                        date = datetime.date.fromtimestamp(measure['date'])
                        value = m['value']/scale
                        data_from_withings[user][date] = value
    return data_from_withings

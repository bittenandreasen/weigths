import ConfigParser
import urllib

import datetime
import simplejson


WITHINGS_URL = "http://wbsapi.withings.net/measure?action=getmeas&userid={user_id}&publickey={user_public_key}"


def get_data_from_withings():
    config = ConfigParser.ConfigParser()
    config.read(['config_local.cfg'])
    users = config.get('WITHINGS', 'users').split(',')
    user_ids = config.get('WITHINGS', 'user_ids').split(',')
    user_public_keys = config.get('WITHINGS', 'user_public_keys').split(',')
    users = zip(users, user_ids, user_public_keys)
    for (user, user_id, user_public_key) in users:
        url_to_get_info_from_withings = WITHINGS_URL.format(
            user_id=user_id,
            user_public_key=user_public_key
        )
        data = simplejson.loads(urllib.urlopen(url_to_get_info_from_withings).read())
        data_from_withings = []
        for measure in data['body']['measuregrps']:
            if measure['category'] == 1:
                for m in measure['measures']:
                    if m['type'] == 1:
                        scale = 10.0 ** (-m['unit'])
                        date = datetime.date.fromtimestamp(measure['date'])
                        value = m['value']/scale
                        data_from_withings += [{'user': user, 'date': date, 'weight': value}]
    return data_from_withings


def get_and_store_data_from_withings():
    withings_data = get_data_from_withings()
    for measure in withings_data:
        print(measure)
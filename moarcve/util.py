import datetime
import pytz
import re
from collections import namedtuple
from moarcve.core import log

__SAFE_PROPERTY__ = [
    'id', 'cve_id', 'year', 'summary', 'cvss', 'last_modified_datetime']
__FORMAT_GMT__ = '%a, %d %b %Y %H:%M:%S GMT'


def utcnow():
    return datetime.datetime.now(tz=pytz.utc)


pat_cve = re.compile(
                     '^(cve)'
                     '(_|-|.|\s)'
                     '(\d+)'
                     '(_|-|.|\s)'
                     '(\d+)$', re.IGNORECASE)


def cleantxt(txt):
    if txt is None or txt == '':
        return ''
    return txt.strip()

cve_tuple = namedtuple('cve', ('year', 'cve_id'))
cve_tuple.as_string = lambda s: ('CVE-%s-%s' % (s[0], s[1])).upper()


def get_cve_tuple(txt):
    txt = cleantxt(txt)
    m = pat_cve.match(txt)
    if not m:
        return None
    return cve_tuple(int(m.group(3)), int(m.group(5)))

if __name__ == '__main__':
    t1 = get_cve_tuple('CVE-2002-1986')
    t2 = get_cve_tuple('CVE-2002-1986')
    t3 = get_cve_tuple('CVE-2004-1986')

    print(t1, t2, t3)
    print(t1.as_string())
    if t1 == t2:
        print('%s == %s' % (t1, t2))
    if t1 != t3:
        print('%s != %s' % (t1, t3))


def column_convert(column, output):
    """Convertit les données en fonction du type de colonne
    """
    if output is None:
        return None
    if column.name in ['until', 'created_on']:
        return output.strftime(__FORMAT_GMT__)
    return output


def sgetattr(resource, name):
    try:
        return getattr(resource, name)
    except Exception as e:
        log.critical('Error: %s', e)
    return None


def res2dct(resource, safe=True):
    """Database row to dictionary"""
    data = {}
    if safe is True:
        def skipit(name):
            if name not in __SAFE_PROPERTY__:
                return True
            return False
    else:
        def skipit(name):
            return False
    for column in resource.__table__.columns:
        if skipit(column.name):
            continue
        data[column.name] = column_convert(
            column, sgetattr(resource, column.name))
    return data

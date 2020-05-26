import urllib.parse
import json
from lxml import etree
import urllib


class QueryBuilder:

    def __init__(self, entity: str):
        self._query = None
        self._action = None
        self._fetchxml = None
        self._selects = None
        self._filters = []
        self._expand = None
        self._order = []
        self._top = None
        self._skip = None
        self._guid = None
        self._data = None

        if not isinstance(entity, (str)):
            raise Exception('Must pass a string as entity')
        self._entity = entity

    def guid(self, guid: str):
        if not isinstance(guid, (str)):
            raise Exception('Must pass a string to guid()')
        self._guid = guid
        return self

    def action(self, action: str):
        if not isinstance(action, (str)):
            raise Exception('Must pass a string to action()')
        self._action = action
        return self

    def select(self, l: list):
        if not isinstance(l, (list)):
            raise Exception('Must pass a list to select()')
        self._selects = l
        return self

    def filter(self, field=None, comp=None, value=None, type=None, logop='and'):
        if field is None or comp is None or value is None or type is None:
            raise Exception('Must set field, comp, value and type')

        if logop not in ['and', 'or', 'and not']:
            raise Exception('Logical operator must be one of: and/or/and-not')

        if comp not in ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'startswith', 'in', 'contains', 'between', 'notin']:
            raise Exception('Invalid comparison type')

        self._filters.append({
            'by': field,
            'comp': comp,
            'value': value,
            'type': type,
            'logop': logop
        })

        return self

    def expand(self, l: list):
        if not isinstance(l, (list)):
            raise Exception('Must pass a list to expand()')
        self._expand = l
        return self

    def order(self, by: list, mode: str):
        if not isinstance(by, (list)):
            raise Exception('Must pass a list to order() as by')

        if mode not in ['asc', 'desc']:
            raise Exception('Mode must be one of asc or desc')

        self._order.append({
            'by': by,
            'mode': mode
        })

        return self

    def limit(self, skip: int, top: int):
        if not isinstance(skip, (int)):
            raise Exception('Must pass an int to limit() as skip')
        if not isinstance(top, (int)):
            raise Exception('Must pass an int to limit() as top')
        self._top = top
        if skip > 0:
            self._skip = skip
        return self

    def fetchxml(self, xml: str):
        if self._action is not None or self._action is not None or len(self._filters) > 0:
            raise Exception('FetchXML can not be used in conjunction with other query methods')

        self._fetchxml = xml
        return self

    def update_fetchxml_cookie(self, cookie: str, page: int):
        if self._fetchxml is None:
            raise Exception('No FetchXML has been set')

        try:
            xml = etree.fromstring(self._fetchxml)
            cook = etree.fromstring(cookie)
            lecookie = urllib.parse.unquote(urllib.parse.unquote(cook.get('pagingcookie')))
            xml.set('page', '%d' % page)
            xml.set('paging-cookie', lecookie)
            self._fetchxml = etree.tostring(xml)
        except Exception as e:
            raise e

    def data(self, data):
        self._data = data
        return self

    def _buildentity(self):
        if self._entity is None:
            raise Exception('Entity must be set')

        self._query = str(self._entity)

    def _buildguid(self):
        self._query += "(%s)" % self._guid

    def _buildaction(self):
        self._query += "/Microsoft.Dynamics.CRM.%s" % self._action

    def _buildfetchxml(self):
        self._query += "fetchXml=%s" % urllib.parse.quote_plus(self._fetchxml)

    def _buildselects(self):
        self._query += "$select=%s" % ",".join(self._selects)

    def _buildfilters(self):
        if self._query[-1:] != "?":
            self._query += "&"

        self._query += "$filter="
        _first = True
        for fil in self._filters:
            if _first is not True:
                self._query += " %s " % fil['logop']
            _first = False

            if fil['comp'] == 'startswith':
                self._query += "startswith(%s, '%s')" % (fil['by'], urllib.parse.quote_plus(str(fil['value'])))
            elif fil['comp'] == 'between':
                self._query += "Microsoft.Dynamics.CRM.Between(PropertyName='%s', PropertyValues=['%s','%s'])" %\
                               (fil['by'], urllib.parse.quote_plus(str(fil['value'][0])),
                                urllib.parse.quote_plus(str(fil['value'][1])))
            elif fil['comp'] == 'in':
                self._query += "Microsoft.Dynamics.CRM.In(PropertyName='%s',PropertyValues=['%s'])" %\
                               (fil['by'], "','".join(fil['value']))
            elif fil['comp'] == 'notin':
                self._query += "Microsoft.Dynamics.CRM.NotIn(PropertyName='%s',PropertyValues=['%s'])" %\
                               (fil['by'], "','".join(fil['value']))
            elif fil['comp'] == 'contains':
                self._query += "contains(%s, '%s')" % (fil['by'], urllib.parse.quote_plus(fil['value']))
            else:
                self._query += "%s %s " % (fil['by'], fil['comp'])
                if fil['type'] == 'str':
                    self._query += "'%s'" % urllib.parse.quote_plus(fil['value'])
                elif fil['type'] == 'bool':
                    if fil['value'] is True:
                        self._query += "true"
                    else:
                        self._query += "false"
                else:
                    self._query += "%s" % fil['value']

    def _buildexpand(self):
        if self._query[-1:] != "?":
            self._query += "&"

        self._query += "$expand=%s" % ",".join(self._expand)

    def _buildorder(self):
        if self._query[-1:] != "?":
            self._query += "&"

        self._query += "$orderby="
        first = True
        for o in self._order:
            if first is False:
                self._query += ","
            self._query += "%s %s" % (",".join(o['by']), o['mode'])
            first = False

    def _buildlimit(self):
        if self._query[-1:] != "?":
            self._query += "&"

        self._query += "$top=%d" % self._top

        if self._skip is not None:
            self._query += "&$skip=%d" % self._skip

    def buildquery(self):
        self._buildentity()

        if self._guid is not None:
            self._buildguid()

        if self._action is not None:
            self._buildaction()

        self._query += '?'

        if self._fetchxml is not None:
            self._buildfetchxml()
            return self._query

        if self._selects is not None:
            self._buildselects()

        if len(self._filters) > 0:
            self._buildfilters()

        if self._expand is not None:
            self._buildexpand()

        if len(self._order) > 0:
            self._buildorder()

        if self._top is not None:
            self._buildlimit()

        return self._query.rstrip("?")

    def getdata(self):
        try:
            return json.dumps(self._data)
        except TypeError:
            raise Exception('Unable to encode data')

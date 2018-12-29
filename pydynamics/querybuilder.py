import urllib.parse


class QueryBuilder:

    def __init__(self):
        self._query = None
        self._entity = None
        self._action = None
        self._fetchxml = None
        self._selects = None
        self._filters = []
        self._expand = None
        self._order = []
        self._top = None
        self._skip = None

    def entity(self, entity: str):
        if not isinstance(entity, (str)):
            raise Exception('Must pass a string to entity()')
        self._entity = entity
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

    def _buildentity(self):
        if self._entity is None:
            raise Exception('Entity must be set')

        self._query = self._entity

    def _buildaction(self):
        self._query += '/Microsoft.Dynamics.CRM.' + self._action;

    def _buildfetchxml(self):
        self._query += 'fetchXml='+urllib.parse.quote_plus(self._fetchxml)

    def _buildselects(self):
        self._query += '$select='
        self._query += ','.join(self._selects)

    def _buildfilters(self):
        if self._query[-1:] != "?":
            self._query += '&'

        self._query += "$filter="
        _first = True
        ftext = ""
        for filter in self._filters:
            if _first is not True:
                ftext += " "+filter['logop']+" "
            _first = False

            if filter['comp'] == 'startswith':
                ftext += "startswith("+filter['by']+", '"+urllib.parse.quote_plus(str(filter['value']))+"')"
            elif filter['comp'] == 'between':
                ftext += "Microsoft.Dynamics.CRM.Between(PropertyName='"+filter['by']+"', PropertyValues=['"+urllib.parse.quote_plus(str(filter['value'][0]))+"','"+urllib.parse.quote_plus(str(filter['value'][1]))+"'])"
            elif filter['comp'] == 'in':
                ftext += "Microsoft.Dynamics.CRM.In(PropertyName='"+filter['by']+"',PropertyValues=['"+"','".join(filter['value'])+"'])"
            elif filter['comp'] == 'notin':
                ftext += "Microsoft.Dynamics.CRM.NotIn(PropertyName='"+filter['by']+"',PropertyValues=['"+"','".join(filter['value'])+"'])"
            elif filter['comp'] == 'contains':
                ftext += "contains("+filter['by']+", '"+urllib.parse.quote_plus(filter['value'])+"')"
            else:
                ftext += filter['by'] + " " + filter['comp'] + " "
                if filter['type'] == 'str':
                    ftext += "'"+urllib.parse.quote_plus(filter['value'])+"'"
                elif filter['type'] == 'bool':
                    if filter['value'] is True:
                        ftext += "true"
                    else:
                        ftext += "false"
                else:
                    ftext += filter['value']

            self._query += urllib.parse.quote_plus(ftext)

    def _buildexpand(self):
        if self._query[-1:] != "?":
            self._query += '&'

        self._query += 'expand='
        self._query += ','.join(self._expand)

    def _buildorder(self):
        if self._query[-1:] != "?":
            self._query += '&'

        self._query += "$orderby="
        first = True
        for o in self._order:
            if first is False:
                self._query += ","
            self._query += ",".join(o['by'])+" "+o['mode']
            first = False

    def _buildlimit(self):
        if self._query[-1:] != "?":
            self._query += '&'

        self._query += "$top="+str(self._top)

        if self._skip is not None:
            self._query += "&$skip="+str(self._skip)

    def buildquery(self):
        self._buildentity()
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

        return self._query

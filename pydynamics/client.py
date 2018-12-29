import requests
import pydynamics


class Client:

    def __init__(self, token, endpoint):
        self._token = str(token)
        self._endpoint = endpoint
        self._headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'OData-Version': '4.0',
                         'OData-MaxVersion': '4.0', 'prefer': 'odata.include-annotations=*',
                         'Authorization': 'Bearer '+self._token}

    def select(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception('Query must be of type QueryBuilder')

        resp = requests.get(self._endpoint + query.buildquery(), headers=self._headers)
        results = resp.json()['value']

        nextlink = None
        if '@odata.nextLink' in resp.json():
            nextlink = resp.json()['@odata.nextLink']

        while nextlink is not None:
            resp = requests.get(nextlink, headers=self._headers)
            results = results + resp.json()['value']
            if '@odata.nextLink' in resp.json():
                nextlink = resp.json()['@odata.nextLink']
            else:
                nextlink = None


        return results
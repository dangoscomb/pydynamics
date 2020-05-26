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
        results = []
        if resp.status_code in [404, 204]:
            return results
        elif resp.status_code == 200:
            if 'value' in resp.json():
                results += resp.json()['value']
            else:
                results.append(resp.json())

            nextlink = None
            if '@odata.nextLink' in resp.json():
                nextlink = resp.json()['@odata.nextLink']

            while nextlink is not None:
                resp = requests.get(nextlink, headers=self._headers)
                if resp.status_code != 200:
                    raise Exception("Failed to query nextLink")
                results = results + resp.json()['value']
                if '@odata.nextLink' in resp.json():
                    nextlink = resp.json()['@odata.nextLink']
                else:
                    nextlink = None

            cookie = None
            page = 2
            if '@Microsoft.Dynamics.CRM.fetchxmlpagingcookie' in resp.json():
                cookie = resp.json()['@Microsoft.Dynamics.CRM.fetchxmlpagingcookie']
                query.update_fetchxml_cookie(cookie, page)

            while cookie is not None:
                page += 1
                resp = requests.get(self._endpoint + query.buildquery(), headers=self._headers)
                if resp.status_code != 200:
                    raise Exception("Failed to query next page")
                results = results + resp.json()['value']
                if '@Microsoft.Dynamics.CRM.fetchxmlpagingcookie' in resp.json():
                    cookie = resp.json()['@Microsoft.Dynamics.CRM.fetchxmlpagingcookie']
                    query.update_fetchxml_cookie(cookie, page)
                else:
                    cookie = None

            return results
        else:
            raise Exception("Bad Request")

    def update(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception("Query must be of type QueryBuilder")

        resp = requests.patch(self._endpoint + query.buildquery(), data=query.getdata(), headers=self._headers)
        if resp.status_code == 204:
            return True
        elif resp.status_code == 404:
            return False
        elif resp.status_code > 400:
            raise Exception("Bad Request")
        else:
            return False

    def create(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception("Query must be of type QueryBuilder")

        resp = requests.post(self._endpoint + query.buildquery(), data=query.getdata(), headers=self._headers)

        if resp.status_code == 204:
            guidstring = resp.headers['OData-EntityId']
            return guidstring[-37:-1]
        else:
            raise Exception('Create failed')

    def delete(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception("Query must be of type QueryBuilder")

        resp = requests.delete(self._endpoint + query.buildquery(), headers=self._headers)
        if resp.status_code == 204:
            return True
        elif resp.status_code == 404:
            return False
        elif resp.status_code > 400:
            raise Exception("Bad Request")
        else:
            return False

    def associate(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception("Query must be of type QueryBuilder")

        resp = requests.post(self._endpoint + query.buildquery(), data=query.getdata(), headers=self._headers)
        if resp.status_code == 204:
            return True
        elif resp.status_code == 404:
            return False
        elif resp.status_code > 400:
            raise Exception("Bad Request")
        else:
            return False

    def action(self, query):
        if not isinstance(query, pydynamics.querybuilder.QueryBuilder):
            raise Exception("Query must be of type QueryBuilder")

        resp = requests.post(self._endpoint + query.buildquery(), data=query.getdata(), headers=self._headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception("Bad Request")

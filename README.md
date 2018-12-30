# PyDynamics

Client and Query Builder for On-Premise Microsoft Dynamics CRM.

## Getting an Auth Token
The first task would be to fetch an authentication token. To do this pass your username and password to the token.get() function along with the URL of your CRM instance.
```python
from pydynamics import token
tok = token.get('https://crm.domain.com/', 'DOMAIN\\username', 'password')
```
The returned token can then be used in subsequent client calls.

## Create a client instance
Pass the token generated above to the Client constructor along with the API URL.
```python
from pydynamics.client import Client
client = Client(tok, 'https://crm.domain.com/INSTANCE/api/data/v8.1/')
```

## Building Queries
The package includes a query builder.

### Select a single item
The below example returns a single contact record, selected on its GUID and selects 3 specific fields to return. the select() part is optional, a default field set will be returned if it is omitted.
```python
from pydynamics.querybuilder import QueryBuilder
q = QueryBuilder('contacts').guid('1bf1c4cf-1ed1-e311-941c-0050568a018c').\
    select(['firstname','lastname', 'emailaddress1'])
result = client.select(q)
```

### Select based on filters
The below example returns the first 2, based on the limit(), contacts that contain the string "flowplex" within the emailaddress1 field and implements ordering and return field selection.
```python
from pydynamics.querybuilder import QueryBuilder
q = QueryBuilder('contacts').\
    filter('emailaddress1', 'contains', 'flowplex', 'str').\
    select(['firstname','lastname', 'emailaddress1']).\
    order(['lastname'],'asc').limit(0 ,2)
result = client.select(q)
```

### Create a record
The below creates a contact entity with the data provided to the query builder. The GUID of the new item will be returned if successful.
```python
from pydynamics.querybuilder import QueryBuilder
q = QueryBuilder('contacts').data({'firstname': 'Dan', 'lastname': 'Test', 'emailaddress1': 'dan@fdsdsds.com'})
guid = client.create(q)
```

### Update a record
The below updates the firstname field on the specific contact record.
```python
from pydynamics.querybuilder import QueryBuilder
q = QueryBuilder('contacts').guid('1bf1c4cf-1ed1-e311-941c-0050568a018c').data({'firstname': 'Daniel'})
client.update(q)
```

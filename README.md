# PyDynamics

Client and Query Builder for On-Premise Microsoft Dynamics CRM.

## Example

```python
from pydynamics import token
from pydynamics.querybuilder import QueryBuilder
from pydynamics.client import Client

tok = token.get('https://crm.domain.com/', 'DOMAIN\\username', 'password')

tq = QueryBuilder('contacts').\
    filter('emailaddress1', 'contains', 'goscomb', 'str').\
    select(['firstname','lastname', 'emailaddress1']).\
    order(['lastname'],'asc').limit(0 ,2)
    
client = Client(tok, 'https://crm.domain.com/INSTANCE/api/data/v8.1/')
ret = client.select(tq)

for c in ret:
    print(c['lastname'])
    
q2 = QueryBuilder('contacts').guid('1bf1c4cf-1ed1-e311-941c-0050568a018c').\
    select(['firstname','lastname', 'emailaddress1'])
r2 = client.select(q2)

for c in r2:
    print(c['lastname'])

```
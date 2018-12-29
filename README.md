# PyDynamics

Client and Query Builder for On-Premise Microsoft Dynamics CRM.

## Example

```python
from pydynamics import token
from pydynamics.querybuilder import QueryBuilder
from pydynamics.client import Client

tok = token.get('https://crm.domain.com/', 'DOMAIN\\username', 'password')

tq = QueryBuilder().entity('contacts').\
    filter('emailaddress1', 'contains', 'goscomb', 'str').\
    select(['firstname','lastname', 'emailaddress1']).\
    order(['lastname'],'asc').limit(0 ,2)
    
client = Client(tok, 'https://crm.domain.com/INSTANCE/api/data/v8.1/')
ret = client.select(tq)

for c in ret:
    print(c['lastname'])

```
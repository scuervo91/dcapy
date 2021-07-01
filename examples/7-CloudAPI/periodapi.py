from dcapy.auth import Credential
from dcapy.schedule import Period

cred = Credential()
cred.login('scuervo91','Fenicia1703')

p = Period()

p.get_db('820f6684-1e30-4d55-bff6-ae4363b9d000',cred)

print(p)


print(p.generate_forecast())

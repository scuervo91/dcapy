from dcapy.auth import Credential
from dcapy.schedule import Period

cred = Credential()
cred.login('pepitoperez','1234')

p = Period()

p.get_db('2032b907-d01f-411b-9ba1-c430f52fbadc',cred)

print(p)


print(p.generate_forecast())

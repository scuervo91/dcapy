from dcapy.auth import Credential
from dcapy.schedule import Period

cred = Credential()
cred.login('scuervo91','Fenicia1703')

df = cred.get_models_info()

print(df)

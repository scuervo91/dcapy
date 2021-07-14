from sqlalchemy import schema
from dcapy.auth import Credential
from dcapy.schedule import Period

cred = Credential()
cred.login('scuervo91','Fenicia1703')

df = cred.get_models_info()

print(df)


df2 = cred.get_models_info(schema=['period','well'])

print(df2)
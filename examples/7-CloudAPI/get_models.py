from sqlalchemy import schema
from dcapy.auth import Credential
from dcapy.schedule import Period

cred = Credential()
cred.login('user','password')

df = cred.get_models_info()

print(df)


df2 = cred.get_models_info(schema=['period','well'])

print(df2)
from pydantic import BaseModel, Field, HttpUrl
import requests
import json

api_url = 'http://127.0.0.1:8000/'

class Credential(BaseModel):
    url: HttpUrl = Field(api_url, const=True)
    token: str = Field(None)
    
    class Config:
        extra = 'forbid'
        validate_assignment = True
        
    def get_user(self):
        end_point = 'admin/me'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }       
        try:
            r = requests.get(f'{self.url}{end_point}', headers=headers)
            r.raise_for_status()
            return json.loads(r.text)
        except requests.exceptions.HTTPError as err:
            print(err)
        
        
    
    def login(self,username,password):
        end_point = 'admin/login'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'username': username,
            'password': password,
        }
    
        try:
            r = requests.post(f'{self.url}{end_point}', headers=headers, data=data)
            r.raise_for_status()
            d = json.loads(r.text)
            self.token = d['access_token']
            return d
        except requests.exceptions.HTTPError as err:
            print(err)
        


        
        
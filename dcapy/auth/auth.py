from pydantic import BaseModel, Field, HttpUrl
import requests
import json
import pandas as pd
from typing import List, Union

api_url = 'https://dcapyapi.herokuapp.com/'
#api_url = 'http://127.0.0.1:8000/'


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
            
    def get_models_info(self, schema:Union[str,List]=None):
        
        list_endpoints = []
        if schema is None:
            list_endpoints.append('api/v1/models/')
        else:
            if isinstance(schema, str):
                list_endpoints.append(f'api/v1/models/{schema}')
            else:
                for i in schema:
                    list_endpoints.append(f'api/v1/models/{i}')

        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }  

        df = pd.DataFrame()
        try:
            for end_point in list_endpoints:
                r = requests.get(f'{self.url}{end_point}', headers=headers)
                r.raise_for_status()
                df = df.append(pd.read_json(r.text,orient='records'))
        except requests.exceptions.HTTPError as err:
            print(err)
            
        return df
        
        
        
        
        


        
        
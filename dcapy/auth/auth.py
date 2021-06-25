from pydantic import BaseModel, Field, HttpUrl

end_point = 'http://127.0.0.1:8000/'

class Credential(BaseModel):
    end_point: HttpUrl = Field(end_point, const=True)
    token: str = Field(None)
    
    class Config:
        extra = 'forbid'
        validate_assignment = True
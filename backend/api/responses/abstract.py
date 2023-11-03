from datetime import datetime
from pydantic import BaseModel


class Response(BaseModel):
     class Config:
        json_encoders = {
            datetime: lambda x: str(x)
        }

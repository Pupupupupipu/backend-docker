from typing import Union, Annotated
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, String, Integer, Identity, Sequence, Float, Boolean, ForeignKey, MetaData, DATETIME, ARRAY, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id_user = Column(Integer, primary_key=True)
    name = Column(String)
    district = Column(ARRAY(String))
    active_order = Column(JSONB)

class Main_User_1(BaseModel):
    id_user: Annotated[Union[int, None], Field(default=100, ge=1, lt=288)] = None

class Main_User_2(Main_User_1):
    name: Union[str, None] = None
    district: Union[list, None] = None

class Main_User_3(BaseModel):
    name: Union[str, None] = None
    district: Union[list, None] = None

class Main_User_5(Main_User_1):
    name: Union[str, None] = None
    district: Union[list, None] = None
    active_order: Union[dict, None] = None

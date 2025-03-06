import enum
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import DeclarativeBase

from coolNewLanguage.src import consts


class Base(DeclarativeBase):
    pass


class ContentTypes(enum.Enum):
    PDF = "pdf"


class UserContent(Base):
    __tablename__ = consts.CONTENT_REGISTRY_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_name = Column(String, nullable=False)
    content_file_name = Column(String, nullable=False)
    content_type = Column(Enum(ContentTypes), nullable=False)

from sqlalchemy import (
    Column,
    Integer,
    Sequence,
    String,
)

from project.database import Base


class Example(Base):
    __tablename__: str = "examples"

    id = Column(Integer, Sequence("examples_id_seq"), primary_key=True)
    
    code = Column(String)
    
    value = Column(String)
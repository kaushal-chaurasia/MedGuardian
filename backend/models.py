from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Drug(Base):
    __tablename__ = "drugs"

    name = Column(String, primary_key=True)
    manufacturer_name = Column(String)
    all_components = Column(String)
    interaction_warning = Column(String)
    side_effects = Column(String)

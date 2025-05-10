from sqlalchemy import Column, Integer, Float, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bin(Base):
    __tablename__ = "bins"

    id = Column(String, primary_key=True, index=True)
    position = Column(JSON)
    fill_level = Column(Float)
    batch_id = Column(String, index=True)

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    optimized_route = Column(JSON)
    total_distance = Column(Float)
    bins_covered = Column(Integer)
    batch_id = Column(String, index=True)
    edges = Column(JSON)
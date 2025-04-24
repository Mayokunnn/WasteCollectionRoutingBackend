from sqlalchemy import Column, Integer, Float, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bin(Base):
    __tablename__ = 'bins'

    id = Column(String, primary_key=True)
    position = Column(JSON)  # Stores coordinates as a JSON (x, y)
    fill_level = Column(Float)  # Percentage fill level (0 to 1)

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    optimized_route = Column(JSON)  # List of bin IDs in the optimized route
    total_distance = Column(Float)
    bins_covered = Column(Integer)

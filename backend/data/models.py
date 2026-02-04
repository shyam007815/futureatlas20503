from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    iso = Column(String, unique=True, index=True)
    iso3 = Column(String, unique=True, index=True)
    name = Column(String)
    region = Column(String)
    exclude_from_leaderboard = Column(Boolean, default=False)
    
    yearly_data = relationship("YearData", back_populates="country")

class YearData(Base):
    __tablename__ = 'yearly_data'
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    year = Column(Integer, index=True)
    gdp = Column(Float)
    population = Column(Float)
    military = Column(Float)
    gsi = Column(Float, default=0.0)
    
    country = relationship("Country", back_populates="yearly_data")

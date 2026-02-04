import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
# Ensure backend dir is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "futureatlas.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        from data.models import Base
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize/Check data
        self._initialize_data()
    
    def get_countries(self) -> List[Dict]:
        from data.models import Country
        session = self.SessionLocal()
        try:
            countries = session.query(Country).all()
            return [
                {
                    "iso": c.iso,
                    "iso3": c.iso3,
                    "name": c.name,
                    "region": c.region,
                    "exclude_from_leaderboard": c.exclude_from_leaderboard
                }
                for c in countries
            ]
        finally:
            session.close()
            
    def get_country_data(self, iso: str) -> Optional[pd.DataFrame]:
        from data.models import Country, YearData
        session = self.SessionLocal()
        try:
            country = session.query(Country).filter(Country.iso3 == iso.lower()).first()
            if not country:
                return None
            
            data = session.query(YearData).filter(YearData.country_id == country.id).order_by(YearData.year).all()
            
            if not data:
                return None

            return pd.DataFrame([{
                'year': d.year,
                'gdp': d.gdp,
                'population': d.population,
                'military': d.military,
                'gsi': d.gsi
            } for d in data])
        finally:
            session.close()

    def get_all_countries_data(self) -> Dict[str, pd.DataFrame]:
        from data.models import Country, YearData
        session = self.SessionLocal()
        try:
            countries = session.query(Country).all()
            all_data = {}
            
            # Fetch all data efficiently
            rows = session.query(YearData).all()
            
            from collections import defaultdict
            data_by_id = defaultdict(list)
            for row in rows:
                data_by_id[row.country_id].append({
                    'year': row.year,
                    'gdp': row.gdp,
                    'population': row.population,
                    'military': row.military,
                    'gsi': row.gsi
                })
                
            for country in countries:
                if country.id in data_by_id:
                    all_data[country.iso3] = pd.DataFrame(data_by_id[country.id])
            
            return all_data
        finally:
            session.close()

    def _initialize_data(self):
        """Initialize database with data if empty"""
        from data.models import Country, YearData
        session = self.SessionLocal()
        try:
            if session.query(Country).first():
                return
            
            print("Initializing database with synthetic data...")
            
            # Full country list
            countries_list = [
                {"iso": "usa", "iso3": "usa", "name": "United States", "region": "North America"},
                {"iso": "chn", "iso3": "chn", "name": "China", "region": "Asia"},
                {"iso": "ind", "iso3": "ind", "name": "India", "region": "Asia"},
                {"iso": "jpn", "iso3": "jpn", "name": "Japan", "region": "Asia"},
                {"iso": "deu", "iso3": "deu", "name": "Germany", "region": "Europe"},
                {"iso": "gbr", "iso3": "gbr", "name": "United Kingdom", "region": "Europe"},
                {"iso": "fra", "iso3": "fra", "name": "France", "region": "Europe"},
                {"iso": "ita", "iso3": "ita", "name": "Italy", "region": "Europe"},
                {"iso": "bra", "iso3": "bra", "name": "Brazil", "region": "South America"},
                {"iso": "can", "iso3": "can", "name": "Canada", "region": "North America"},
                {"iso": "rus", "iso3": "rus", "name": "Russia", "region": "Europe"},
                {"iso": "kor", "iso3": "kor", "name": "South Korea", "region": "Asia"},
                {"iso": "aus", "iso3": "aus", "name": "Australia", "region": "Oceania"},
                {"iso": "mex", "iso3": "mex", "name": "Mexico", "region": "North America"},
                {"iso": "idn", "iso3": "idn", "name": "Indonesia", "region": "Asia"},
                {"iso": "tur", "iso3": "tur", "name": "Turkey", "region": "Asia"},
                {"iso": "sau", "iso3": "sau", "name": "Saudi Arabia", "region": "Middle East"},
                {"iso": "esp", "iso3": "esp", "name": "Spain", "region": "Europe"},
                {"iso": "arg", "iso3": "arg", "name": "Argentina", "region": "South America"},
                {"iso": "pol", "iso3": "pol", "name": "Poland", "region": "Europe"},
                {"iso": "nld", "iso3": "nld", "name": "Netherlands", "region": "Europe"},
                {"iso": "bel", "iso3": "bel", "name": "Belgium", "region": "Europe"},
                {"iso": "swe", "iso3": "swe", "name": "Sweden", "region": "Europe"},
                {"iso": "che", "iso3": "che", "name": "Switzerland", "region": "Europe"},
                {"iso": "sgp", "iso3": "sgp", "name": "Singapore", "region": "Asia"},
                {"iso": "nor", "iso3": "nor", "name": "Norway", "region": "Europe"},
                {"iso": "aut", "iso3": "aut", "name": "Austria", "region": "Europe"},
                {"iso": "are", "iso3": "are", "name": "United Arab Emirates", "region": "Middle East"},
                {"iso": "tha", "iso3": "tha", "name": "Thailand", "region": "Asia"},
                {"iso": "irl", "iso3": "irl", "name": "Ireland", "region": "Europe"},
                {"iso": "pak", "iso3": "pak", "name": "Pakistan", "region": "Asia"},
                {"iso": "bng", "iso3": "bng", "name": "Bangladesh", "region": "Asia"},
                {"iso": "vnm", "iso3": "vnm", "name": "Vietnam", "region": "Asia"},
                {"iso": "nga", "iso3": "nga", "name": "Nigeria", "region": "Africa"},
                {"iso": "zaf", "iso3": "zaf", "name": "South Africa", "region": "Africa"},
                {"iso": "egy", "iso3": "egy", "name": "Egypt", "region": "Africa"},
                {"iso": "isr", "iso3": "isr", "name": "Israel", "region": "Middle East"},
                {"iso": "prt", "iso3": "prt", "name": "Portugal", "region": "Europe"},
                {"iso": "grc", "iso3": "grc", "name": "Greece", "region": "Europe"},
                {"iso": "dnk", "iso3": "dnk", "name": "Denmark", "region": "Europe"},
                {"iso": "fin", "iso3": "fin", "name": "Finland", "region": "Europe"},
                {"iso": "chl", "iso3": "chl", "name": "Chile", "region": "South America"},
                {"iso": "rou", "iso3": "rou", "name": "Romania", "region": "Europe"},
                {"iso": "cze", "iso3": "cze", "name": "Czech Republic", "region": "Europe"},
                {"iso": "hun", "iso3": "hun", "name": "Hungary", "region": "Europe"},
                {"iso": "nzl", "iso3": "nzl", "name": "New Zealand", "region": "Oceania"},
                {"iso": "per", "iso3": "per", "name": "Peru", "region": "South America"},
                {"iso": "kaz", "iso3": "kaz", "name": "Kazakhstan", "region": "Asia"},
                {"iso": "qat", "iso3": "qat", "name": "Qatar", "region": "Middle East"},
                {"iso": "ukr", "iso3": "ukr", "name": "Ukraine", "region": "Europe"},
                {"iso": "col", "iso3": "col", "name": "Colombia", "region": "South America"},
                {"iso": "mys", "iso3": "mys", "name": "Malaysia", "region": "Asia"},
                {"iso": "phl", "iso3": "phl", "name": "Philippines", "region": "Asia"},
                {"iso": "irn", "iso3": "irn", "name": "Iran", "region": "Middle East"},
                {"iso": "irq", "iso3": "irq", "name": "Iraq", "region": "Middle East"},
                {"iso": "afg", "iso3": "afg", "name": "Afghanistan", "region": "Asia"},
                {"iso": "mmr", "iso3": "mmr", "name": "Myanmar", "region": "Asia"},
                {"iso": "ken", "iso3": "ken", "name": "Kenya", "region": "Africa"},
                {"iso": "uga", "iso3": "uga", "name": "Uganda", "region": "Africa"},
                {"iso": "tza", "iso3": "tza", "name": "Tanzania", "region": "Africa"},
                {"iso": "gha", "iso3": "gha", "name": "Ghana", "region": "Africa"},
                {"iso": "eth", "iso3": "eth", "name": "Ethiopia", "region": "Africa"},
                {"iso": "dza", "iso3": "dza", "name": "Algeria", "region": "Africa"},
                {"iso": "mar", "iso3": "mar", "name": "Morocco", "region": "Africa"},
                {"iso": "sdn", "iso3": "sdn", "name": "Sudan", "region": "Africa"},
                {"iso": "ven", "iso3": "ven", "name": "Venezuela", "region": "South America"},
                {"iso": "ecu", "iso3": "ecu", "name": "Ecuador", "region": "South America"},
                {"iso": "bol", "iso3": "bol", "name": "Bolivia", "region": "South America"},
                {"iso": "ury", "iso3": "ury", "name": "Uruguay", "region": "South America"},
                {"iso": "par", "iso3": "par", "name": "Paraguay", "region": "South America"},
                {"iso": "gtm", "iso3": "gtm", "name": "Guatemala", "region": "North America"},
                {"iso": "cri", "iso3": "cri", "name": "Costa Rica", "region": "North America"},
                {"iso": "pan", "iso3": "pan", "name": "Panama", "region": "North America"},
                {"iso": "dom", "iso3": "dom", "name": "Dominican Republic", "region": "North America"},
                {"iso": "cub", "iso3": "cub", "name": "Cuba", "region": "North America"},
                {"iso": "hnd", "iso3": "hnd", "name": "Honduras", "region": "North America"},
                {"iso": "slv", "iso3": "slv", "name": "El Salvador", "region": "North America"},
                {"iso": "nic", "iso3": "nic", "name": "Nicaragua", "region": "North America"},
                {"iso": "jam", "iso3": "jam", "name": "Jamaica", "region": "North America"},
                {"iso": "tto", "iso3": "tto", "name": "Trinidad and Tobago", "region": "North America"},
                {"iso": "lbn", "iso3": "lbn", "name": "Lebanon", "region": "Middle East"},
                {"iso": "jor", "iso3": "jor", "name": "Jordan", "region": "Middle East"},
                {"iso": "syr", "iso3": "syr", "name": "Syria", "region": "Middle East"},
                {"iso": "yem", "iso3": "yem", "name": "Yemen", "region": "Middle East"},
                {"iso": "omn", "iso3": "omn", "name": "Oman", "region": "Middle East"},
                {"iso": "kwt", "iso3": "kwt", "name": "Kuwait", "region": "Middle East"},
                {"iso": "bhr", "iso3": "bhr", "name": "Bahrain", "region": "Middle East"},
                {"iso": "lka", "iso3": "lka", "name": "Sri Lanka", "region": "Asia"},
                {"iso": "npl", "iso3": "npl", "name": "Nepal", "region": "Asia"},
                {"iso": "khm", "iso3": "khm", "name": "Cambodia", "region": "Asia"},
                {"iso": "lao", "iso3": "lao", "name": "Laos", "region": "Asia"},
                {"iso": "mng", "iso3": "mng", "name": "Mongolia", "region": "Asia"},
                {"iso": "uzb", "iso3": "uzb", "name": "Uzbekistan", "region": "Asia"},
                {"iso": "tjk", "iso3": "tjk", "name": "Tajikistan", "region": "Asia"},
                {"iso": "kgz", "iso3": "kgz", "name": "Kyrgyzstan", "region": "Asia"},
                {"iso": "tkm", "iso3": "tkm", "name": "Turkmenistan", "region": "Asia"},
                {"iso": "aze", "iso3": "aze", "name": "Azerbaijan", "region": "Asia"},
                {"iso": "arm", "iso3": "arm", "name": "Armenia", "region": "Asia"},
                {"iso": "geo", "iso3": "geo", "name": "Georgia", "region": "Asia"},
                {"iso": "mdv", "iso3": "mdv", "name": "Maldives", "region": "Asia"},
                {"iso": "btn", "iso3": "btn", "name": "Bhutan", "region": "Asia"},
                {"iso": "brn", "iso3": "brn", "name": "Brunei", "region": "Asia"},
                {"iso": "png", "iso3": "png", "name": "Papua New Guinea", "region": "Oceania"},
                {"iso": "fji", "iso3": "fji", "name": "Fiji", "region": "Oceania"},
                {"iso": "ncl", "iso3": "ncl", "name": "New Caledonia", "region": "Oceania"},
                {"iso": "pyf", "iso3": "pyf", "name": "French Polynesia", "region": "Oceania"},
                {"iso": "blr", "iso3": "blr", "name": "Belarus", "region": "Europe"},
                {"iso": "bgr", "iso3": "bgr", "name": "Bulgaria", "region": "Europe"},
                {"iso": "hrv", "iso3": "hrv", "name": "Croatia", "region": "Europe"},
                {"iso": "srb", "iso3": "srb", "name": "Serbia", "region": "Europe"},
                {"iso": "slo", "iso3": "slo", "name": "Slovenia", "region": "Europe"},
                {"iso": "svk", "iso3": "svk", "name": "Slovakia", "region": "Europe"},
                {"iso": "lva", "iso3": "lva", "name": "Latvia", "region": "Europe"},
                {"iso": "ltu", "iso3": "ltu", "name": "Lithuania", "region": "Europe"},
                {"iso": "est", "iso3": "est", "name": "Estonia", "region": "Europe"},
                {"iso": "isl", "iso3": "isl", "name": "Iceland", "region": "Europe"},
                {"iso": "lux", "iso3": "lux", "name": "Luxembourg", "region": "Europe"},
                {"iso": "mda", "iso3": "mda", "name": "Moldova", "region": "Europe"},
                {"iso": "mkd", "iso3": "mkd", "name": "North Macedonia", "region": "Europe"},
                {"iso": "alb", "iso3": "alb", "name": "Albania", "region": "Europe"},
                {"iso": "bih", "iso3": "bih", "name": "Bosnia and Herzegovina", "region": "Europe"},
                {"iso": "mne", "iso3": "mne", "name": "Montenegro", "region": "Europe"},
                {"iso": "xkx", "iso3": "xkx", "name": "Kosovo", "region": "Europe"},
                {"iso": "mli", "iso3": "mli", "name": "Mali", "region": "Africa"},
                {"iso": "bfa", "iso3": "bfa", "name": "Burkina Faso", "region": "Africa"},
                {"iso": "ner", "iso3": "ner", "name": "Niger", "region": "Africa"},
                {"iso": "sen", "iso3": "sen", "name": "Senegal", "region": "Africa"},
                {"iso": "gnb", "iso3": "gnb", "name": "Guinea-Bissau", "region": "Africa"},
                {"iso": "gin", "iso3": "gin", "name": "Guinea", "region": "Africa"},
                {"iso": "sle", "iso3": "sle", "name": "Sierra Leone", "region": "Africa"},
                {"iso": "lbr", "iso3": "lbr", "name": "Liberia", "region": "Africa"},
                {"iso": "civ", "iso3": "civ", "name": "Ivory Coast", "region": "Africa"},
                {"iso": "mrt", "iso3": "mrt", "name": "Mauritania", "region": "Africa"},
                {"iso": "gmb", "iso3": "gmb", "name": "Gambia", "region": "Africa"},
                {"iso": "ben", "iso3": "ben", "name": "Benin", "region": "Africa"},
                {"iso": "tgo", "iso3": "tgo", "name": "Togo", "region": "Africa"},
                {"iso": "cmr", "iso3": "cmr", "name": "Cameroon", "region": "Africa"},
                {"iso": "caf", "iso3": "caf", "name": "Central African Republic", "region": "Africa"},
                {"iso": "tcd", "iso3": "tcd", "name": "Chad", "region": "Africa"},
                {"iso": "gnq", "iso3": "gnq", "name": "Equatorial Guinea", "region": "Africa"},
                {"iso": "gab", "iso3": "gab", "name": "Gabon", "region": "Africa"},
                {"iso": "cog", "iso3": "cog", "name": "Republic of the Congo", "region": "Africa"},
                {"iso": "cod", "iso3": "cod", "name": "DR Congo", "region": "Africa"},
                {"iso": "rwa", "iso3": "rwa", "name": "Rwanda", "region": "Africa"},
                {"iso": "bdi", "iso3": "bdi", "name": "Burundi", "region": "Africa"},
                {"iso": "som", "iso3": "som", "name": "Somalia", "region": "Africa"},
                {"iso": "dji", "iso3": "dji", "name": "Djibouti", "region": "Africa"},
                {"iso": "ery", "iso3": "ery", "name": "Eritrea", "region": "Africa"},
                {"iso": "mdg", "iso3": "mdg", "name": "Madagascar", "region": "Africa"},
                {"iso": "mus", "iso3": "mus", "name": "Mauritius", "region": "Africa"},
                {"iso": "syc", "iso3": "syc", "name": "Seychelles", "region": "Africa"},
                {"iso": "com", "iso3": "com", "name": "Comoros", "region": "Africa"},
                {"iso": "mwi", "iso3": "mwi", "name": "Malawi", "region": "Africa"},
                {"iso": "zmb", "iso3": "zmb", "name": "Zambia", "region": "Africa"},
                {"iso": "zwe", "iso3": "zwe", "name": "Zimbabwe", "region": "Africa"},
                {"iso": "bwa", "iso3": "bwa", "name": "Botswana", "region": "Africa"},
                {"iso": "nam", "iso3": "nam", "name": "Namibia", "region": "Africa"},
                {"iso": "lso", "iso3": "lso", "name": "Lesotho", "region": "Africa"},
                {"iso": "swz", "iso3": "swz", "name": "Eswatini", "region": "Africa"},
                {"iso": "moz", "iso3": "moz", "name": "Mozambique", "region": "Africa"},
                {"iso": "ago", "iso3": "ago", "name": "Angola", "region": "Africa"},
                {"iso": "tun", "iso3": "tun", "name": "Tunisia", "region": "Africa"},
                {"iso": "lby", "iso3": "lby", "name": "Libya", "region": "Africa"},
                {"iso": "and", "iso3": "and", "name": "Andorra", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "atg", "iso3": "atg", "name": "Antigua and Barbuda", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "bhs", "iso3": "bhs", "name": "Bahamas", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "brb", "iso3": "brb", "name": "Barbados", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "blz", "iso3": "blz", "name": "Belize", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "cpv", "iso3": "cpv", "name": "Cabo Verde", "region": "Africa", "exclude_from_leaderboard": True},
                {"iso": "cyp", "iso3": "cyp", "name": "Cyprus", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "dma", "iso3": "dma", "name": "Dominica", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "tls", "iso3": "tls", "name": "Timor-Leste", "region": "Asia", "exclude_from_leaderboard": True},
                {"iso": "grd", "iso3": "grd", "name": "Grenada", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "guy", "iso3": "guy", "name": "Guyana", "region": "South America", "exclude_from_leaderboard": True},
                {"iso": "hti", "iso3": "hti", "name": "Haiti", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "kir", "iso3": "kir", "name": "Kiribati", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "lie", "iso3": "lie", "name": "Liechtenstein", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "mlt", "iso3": "mlt", "name": "Malta", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "mhl", "iso3": "mhl", "name": "Marshall Islands", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "fsm", "iso3": "fsm", "name": "Micronesia", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "mco", "iso3": "mco", "name": "Monaco", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "nru", "iso3": "nru", "name": "Nauru", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "prk", "iso3": "prk", "name": "North Korea", "region": "Asia", "exclude_from_leaderboard": True},
                {"iso": "plw", "iso3": "plw", "name": "Palau", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "pse", "iso3": "pse", "name": "Palestine", "region": "Middle East", "exclude_from_leaderboard": True},
                {"iso": "kna", "iso3": "kna", "name": "Saint Kitts and Nevis", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "lca", "iso3": "lca", "name": "Saint Lucia", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "vct", "iso3": "vct", "name": "Saint Vincent and the Grenadines", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "wsm", "iso3": "wsm", "name": "Samoa", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "smr", "iso3": "smr", "name": "San Marino", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "stp", "iso3": "stp", "name": "Sao Tome and Principe", "region": "Africa", "exclude_from_leaderboard": True},
                {"iso": "slb", "iso3": "slb", "name": "Solomon Islands", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "ssd", "iso3": "ssd", "name": "South Sudan", "region": "Africa", "exclude_from_leaderboard": True},
                {"iso": "sur", "iso3": "sur", "name": "Suriname", "region": "South America", "exclude_from_leaderboard": True},
                {"iso": "twn", "iso3": "twn", "name": "Taiwan", "region": "Asia", "exclude_from_leaderboard": True},
                {"iso": "ton", "iso3": "ton", "name": "Tonga", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "tuv", "iso3": "tuv", "name": "Tuvalu", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "vut", "iso3": "vut", "name": "Vanuatu", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "vat", "iso3": "vat", "name": "Vatican City", "region": "Europe", "exclude_from_leaderboard": True},
                {"iso": "hkg", "iso3": "hkg", "name": "Hong Kong", "region": "Asia", "exclude_from_leaderboard": True},
                {"iso": "mac", "iso3": "mac", "name": "Macao", "region": "Asia", "exclude_from_leaderboard": True},
                {"iso": "pri", "iso3": "pri", "name": "Puerto Rico", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "grl", "iso3": "grl", "name": "Greenland", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "esh", "iso3": "esh", "name": "Western Sahara", "region": "Africa", "exclude_from_leaderboard": True},
                {"iso": "abw", "iso3": "abw", "name": "Aruba", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "cuw", "iso3": "cuw", "name": "Curacao", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "bmu", "iso3": "bmu", "name": "Bermuda", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "cym", "iso3": "cym", "name": "Cayman Islands", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "gum", "iso3": "gum", "name": "Guam", "region": "Oceania", "exclude_from_leaderboard": True},
                {"iso": "vir", "iso3": "vir", "name": "US Virgin Islands", "region": "North America", "exclude_from_leaderboard": True},
                {"iso": "reu", "iso3": "reu", "name": "Reunion", "region": "Africa", "exclude_from_leaderboard": True},
                {"iso": "glp", "iso3": "glp", "name": "Guadeloupe", "region": "North America", "exclude_from_leaderboard": True},
            ]
            
            # Temporary dict to hold data for GSI calculation
            temp_data = {}
            
            # Generate synthetic historical data (2000-2023) and forecast (2024-2050)
            for country in countries_list:
                iso = country['iso3']
                name = country['name']
                
                # Base values (simplified)
                base_gdp = self._get_base_gdp(name)
                base_pop = self._get_base_pop(name)
                base_mil = self._get_base_mil(name)
                
                years = list(range(2000, 2051))
                data = []
                
                for year in years:
                    if year <= 2023:
                        # Historical trend
                        growth_factor = 1 + (year - 2000) * 0.02
                        gdp = base_gdp * growth_factor
                        pop = base_pop * (1 + (year - 2000) * 0.01)
                        mil = base_mil * growth_factor
                    else:
                        # Forecast
                        forecast_years = year - 2023
                        if name == "China":
                            # China slowing down but still growing
                            gdp = base_gdp * (1.04 ** forecast_years)
                            pop = base_pop * (0.998 ** forecast_years)
                            mil = gdp * 0.02
                        elif name == "India":
                            # High growth
                            gdp = base_gdp * (1.06 ** forecast_years)
                            pop = base_pop * (1.008 ** forecast_years)
                            mil = gdp * 0.025
                        elif name == "United States":
                            gdp = base_gdp * (1.02 ** forecast_years)
                            pop = base_pop * (1.004 ** forecast_years)
                            mil = gdp * 0.032
                        elif name == "Russia":
                            gdp = base_gdp * (1.015 ** forecast_years)
                            pop = base_pop * (0.995 ** forecast_years)
                            mil = base_mil * (1.02 ** forecast_years)
                        else:
                            gdp = base_gdp * (1.025 ** forecast_years)
                            pop = base_pop * (1.005 ** forecast_years)
                            mil = gdp * 0.02
                    
                    data.append({
                        'year': year,
                        'gdp': gdp,
                        'population': pop,
                        'military': mil
                    })
                
                temp_data[iso] = pd.DataFrame(data)

            # Pre-calculate GSI
            try:
                from services.gsi_calculator import GSICalculator
                calculator = GSICalculator()
                
                # Combine all data for batch processing
                all_frames = []
                for iso, df in temp_data.items():
                    df_copy = df.copy()
                    df_copy['iso'] = iso
                    all_frames.append(df_copy)
                
                if all_frames:
                    combined_df = pd.concat(all_frames)
                    processed_frames = []
                    unique_years = sorted(combined_df['year'].unique())
                    
                    for year in unique_years:
                        year_df = combined_df[combined_df['year'] == year].copy()
                        if not year_df.empty:
                            year_df = calculator.calculate_gsi(year_df)
                            processed_frames.append(year_df)
                    
                    if processed_frames:
                        final_df = pd.concat(processed_frames)
                        
                        # Populate Database
                        print("Populating SQLite database...")
                        
                        # Cache countries to get IDs
                        country_map = {}
                        
                        for country_meta in countries_list:
                            db_country = Country(
                                iso=country_meta['iso'],
                                iso3=country_meta['iso3'],
                                name=country_meta['name'],
                                region=country_meta['region'],
                                exclude_from_leaderboard=country_meta.get('exclude_from_leaderboard', False)
                            )
                            session.add(db_country)
                            session.flush()
                            country_map[country_meta['iso3']] = db_country.id
                        
                        # Insert bulk data
                        # We iterate over the final_df
                        bulk_data = []
                        for _, row in final_df.iterrows():
                            # Row has: year, gdp, population, military, year, iso, etc + gsi
                            c_iso = row['iso']
                            if c_iso in country_map:
                                bulk_data.append(YearData(
                                    country_id=country_map[c_iso],
                                    year=int(row['year']),
                                    gdp=float(row['gdp']),
                                    population=float(row['population']),
                                    military=float(row['military']),
                                    gsi=float(row.get('gsi', 0))
                                ))
                        
                        session.bulk_save_objects(bulk_data)
                        session.commit()
                        print(f"Successfully inserted {len(bulk_data)} records.")
                        
            except Exception as e:
                print(f"Error calculating/inserting GSI: {e}")
                import traceback
                traceback.print_exc()
                session.rollback()
            
        except Exception as e:
            print(f"Error initializing DB: {e}")
            session.rollback()
        finally:
            session.close()

    def _get_base_gdp(self, name: str) -> float:
        """Get base GDP in billions USD"""
        base_values = {
            "United States": 26000, "China": 18000, "Japan": 4900, "Germany": 4100, "India": 3400,
            "United Kingdom": 3100, "France": 2800, "Italy": 2100, "Brazil": 1900, "Canada": 2100,
            "Russia": 2200, "South Korea": 1800, "Australia": 1600, "Mexico": 1400, "Indonesia": 1300,
            "Saudi Arabia": 1100, "Netherlands": 1000, "Spain": 1400, "Turkey": 900, "Switzerland": 800,
            "Poland": 700, "Belgium": 600, "Sweden": 600, "Argentina": 650, "Thailand": 550,
            "Norway": 500, "Singapore": 470, "Ireland": 530, "United Arab Emirates": 500, "Pakistan": 350,
            "Bangladesh": 460, "Vietnam": 410, "Nigeria": 480, "South Africa": 420, "Egypt": 470,
            "Philippines": 400, "Malaysia": 430, "Israel": 520, "Portugal": 240, "Greece": 230,
            "Chile": 310, "Romania": 280, "Czech Republic": 290, "Hungary": 180, "New Zealand": 250,
            "Peru": 240, "Kazakhstan": 220, "Qatar": 220, "Ukraine": 200,
            "Andorra": 3, "Antigua and Barbuda": 1.7, "Bahamas": 12, "Barbados": 5, "Belize": 2,
            "Cabo Verde": 2, "Cyprus": 28, "Dominica": 0.6, "Timor-Leste": 2, "Grenada": 1,
            "Guyana": 15, "Haiti": 20, "Kiribati": 0.2, "Liechtenstein": 6, "Malta": 17,
            "Marshall Islands": 0.2, "Micronesia": 0.4, "Monaco": 8, "Nauru": 0.1,
            "North Korea": 30, "Palau": 0.3, "Palestine": 18, "Saint Kitts and Nevis": 1,
            "Saint Lucia": 2, "Saint Vincent and the Grenadines": 0.9, "Samoa": 0.8, "San Marino": 1.5,
            "Sao Tome and Principe": 0.5, "Solomon Islands": 1.6, "South Sudan": 5, "Suriname": 4,
            "Taiwan": 760, "Tonga": 0.5, "Tuvalu": 0.06, "Vanuatu": 1, "Vatican City": 0.1,
            "Hong Kong": 360, "Macao": 30, "Puerto Rico": 110, "Greenland": 3, "Western Sahara": 0.9,
            "Aruba": 3, "Curacao": 3, "Bermuda": 7, "Cayman Islands": 6, "Guam": 6,
            "US Virgin Islands": 4, "Reunion": 5, "Guadeloupe": 9,
        }
        return base_values.get(name, 300)
    
    def _get_base_pop(self, name: str) -> float:
        """Get base population in millions"""
        base_values = {
            "China": 1400, "India": 1400, "United States": 330, "Indonesia": 275, "Pakistan": 240,
            "Brazil": 215, "Bangladesh": 170, "Russia": 145, "Mexico": 130, "Japan": 125,
            "Philippines": 115, "Vietnam": 98, "Ethiopia": 120, "Egypt": 110, "Germany": 83,
            "Turkey": 85, "Iran": 88, "Thailand": 70, "United Kingdom": 67, "France": 68,
            "Italy": 59, "South Africa": 60, "Tanzania": 63, "South Korea": 52, "Spain": 47,
            "Myanmar": 54, "Kenya": 55, "Argentina": 46, "Colombia": 52, "Algeria": 45,
            "Sudan": 46, "Poland": 38, "Ukraine": 43, "Canada": 38, "Iraq": 43,
            "Afghanistan": 41, "Morocco": 37, "Uganda": 48, "Saudi Arabia": 36, "Peru": 34,
            "Malaysia": 33, "Uzbekistan": 35, "Angola": 34, "Venezuela": 29, "Nepal": 30,
            "Mozambique": 32, "Ghana": 32, "Yemen": 31, "Australia": 26, "Madagascar": 29,
            "Cameroon": 28, "North Korea": 26, "Niger": 25, "Sri Lanka": 22, "Burkina Faso": 22,
            "Romania": 19, "Chile": 19, "Netherlands": 17, "Kazakhstan": 19, "Belgium": 12,
            "Greece": 11, "Czech Republic": 11, "Sweden": 10, "Switzerland": 9, "Norway": 5,
            "Singapore": 6, "Ireland": 5, "United Arab Emirates": 10, "New Zealand": 5,
            "Portugal": 10, "Hungary": 10, "Qatar": 3, "Israel": 9, "Nigeria": 220,
            "Andorra": 0.08, "Antigua and Barbuda": 0.1, "Bahamas": 0.4, "Barbados": 0.3, "Belize": 0.4,
            "Cabo Verde": 0.6, "Cyprus": 1.2, "Dominica": 0.07, "Timor-Leste": 1.3, "Grenada": 0.1,
            "Guyana": 0.8, "Haiti": 11, "Kiribati": 0.1, "Liechtenstein": 0.04, "Malta": 0.5,
            "Marshall Islands": 0.06, "Micronesia": 0.1, "Monaco": 0.04, "Nauru": 0.01,
            "North Korea": 26, "Palau": 0.02, "Palestine": 5, "Saint Kitts and Nevis": 0.05,
            "Saint Lucia": 0.18, "Saint Vincent and the Grenadines": 0.1, "Samoa": 0.2, "San Marino": 0.03,
            "Sao Tome and Principe": 0.2, "Solomon Islands": 0.7, "South Sudan": 11, "Suriname": 0.6,
            "Taiwan": 23, "Tonga": 0.1, "Tuvalu": 0.01, "Vanuatu": 0.3, "Vatican City": 0.001,
            "Hong Kong": 7.5, "Macao": 0.7, "Puerto Rico": 3.2, "Greenland": 0.06, "Western Sahara": 0.6,
            "Aruba": 0.1, "Curacao": 0.15, "Bermuda": 0.06, "Cayman Islands": 0.07, "Guam": 0.17,
            "US Virgin Islands": 0.1, "Reunion": 0.9, "Guadeloupe": 0.4,
        }
        return base_values.get(name, 30)
    
    def _get_base_mil(self, name: str) -> float:
        """Get base military expenditure in billions USD"""
        base_values = {
            "United States": 800, "China": 250, "India": 80, "Russia": 85, "United Kingdom": 60,
            "Saudi Arabia": 75, "Germany": 55, "France": 55, "Japan": 50, "South Korea": 45,
            "Italy": 30, "Australia": 32, "Canada": 25, "Turkey": 20, "Israel": 24,
            "Spain": 18, "Netherlands": 15, "Poland": 14, "Brazil": 22, "Taiwan": 17,
            "Singapore": 12, "Sweden": 7, "Norway": 8, "Belgium": 5, "Switzerland": 5,
            "Indonesia": 10, "Pakistan": 12, "Thailand": 7, "Vietnam": 6, "Malaysia": 4,
            "Philippines": 4, "Egypt": 5, "Algeria": 10, "South Africa": 3, "Nigeria": 4,
            "Argentina": 3, "Chile": 5, "Colombia": 4, "Mexico": 7, "Ukraine": 6,
            "Greece": 5, "Portugal": 3, "Romania": 4, "Czech Republic": 3, "Hungary": 2,
            "Qatar": 2, "United Arab Emirates": 23, "Ireland": 1, "New Zealand": 3,
            "Kazakhstan": 2, "Bangladesh": 4, "Taiwan": 19, "North Korea": 4, 
            "Andorra": 0.01, "Antigua and Barbuda": 0.01, "Bahamas": 0.1, "Barbados": 0.05,
            "Cabo Verde": 0.01, "Cyprus": 0.5, "Dominica": 0.01, "Timor-Leste": 0.03, "Grenada": 0.01,
            "Guyana": 0.1, "Haiti": 0.1, "Kiribati": 0.01, "Liechtenstein": 0.01, "Malta": 0.1,
            "Marshall Islands": 0.01, "Micronesia": 0.01, "Monaco": 0.01, "Nauru": 0.01,
            "Palau": 0.01, "Palestine": 0.1, "Saint Kitts and Nevis": 0.01,
            "Saint Lucia": 0.01, "Saint Vincent and the Grenadines": 0.01, "Samoa": 0.01, "San Marino": 0.01,
            "Sao Tome and Principe": 0.01, "Solomon Islands": 0.01, "South Sudan": 1.5, "Suriname": 0.06,
            "Tonga": 0.01, "Tuvalu": 0.01, "Vanuatu": 0.01, "Vatican City": 0.001,
            "Hong Kong": 0.1, "Macao": 0.01, "Puerto Rico": 0.1, "Greenland": 0.1, "Western Sahara": 0.01,
            "Aruba": 0.01, "Curacao": 0.01, "Bermuda": 0.01, "Cayman Islands": 0.01, "Guam": 0.01,
            "US Virgin Islands": 0.01, "Reunion": 0.01, "Guadeloupe": 0.01,
        }
        return base_values.get(name, 2)

# Global database instance
db = Database()

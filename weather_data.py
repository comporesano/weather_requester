from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base


class WeatherData(declarative_base()):
    '''
    Определим модель таблицы:
    * id - Натуральное число, PRIMARY KEY
    * timestamt - Дата
    * temperature - Целочисленное число
    * wind_speed - Целочисленное число
    * wind_direction - Строка
    * pressure - Целочисленное число
    * precipitation_type - Строка
    * precipitation_amount - Целочисленное число
    '''
    __tablename__ = 'weather_data'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    temperature = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String)
    pressure = Column(Float)
    precipitation_type = Column(String)
    precipitation_amount = Column(Float)
from datetime import datetime
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from openpyxl import Workbook
from weather_data import WeatherData


class WeatherRequester:
    '''
    Класс запроса погоды и сохранения данных в бд и экспорта в эксель
    '''
    def __init__(self) -> None:
        # Определим URL-адрес api и параметры
        self.URL = 'https://api.open-meteo.com/v1/forecast'
        self.PARAMS =     params = {'latitude': 55.7032,
                                    'longitude': 37.4166,
                                    'current': ['temperature_2m', 'precipitation', 'rain', 'showers', 'snowfall', 'pressure_msl', 'wind_speed_10m', 'wind_direction_10m'],
                                    'wind_speed_unit': 'ms'
                                    }
        # Создадим соединение с бд
        self.engine = create_async_engine('sqlite+aiosqlite:///weather.db')
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        
    async def request_weather(self) -> dict:
        # Сделаем запрос по URL с соответствующими параметрами
        response = requests.get(self.URL, params=self.PARAMS)
        data = dict(response.json())
        # Обработаем данные с типом осадков
        if int(data['current']['rain']) != 0:
            data['current']['precipitation_type'] = 'RAINY'
        if int(data['current']['showers']) != 0:
            data['current']['precipitation_type'] = 'SHOWERS'
        if int(data['current']['snowfall']) != 0:
            data['current']['precipitation_type'] = 'SNOWFALL'
        else:
            data['current']['precipitation_type'] = 'CLEAR'
        # Обработаем данные с направлением ветра
        if 337.5 < data['current']['wind_direction_10m'] <= 0 or 0 < data['current']['wind_direction_10m'] <= 22.5:
            data['current']['wind_direction_10m'] = 'N'
        elif 22.5 < data['current']['wind_direction_10m'] <= 67.5:
            data['current']['wind_direction_10m'] = 'NE'
        elif 67.6 < data['current']['wind_direction_10m'] <= 112.5:
            data['current']['wind_direction_10m'] = 'E'
        elif 112.5 < data['current']['wind_direction_10m'] <= 157.5:
            data['current']['wind_direction_10m'] = 'SE'
        elif 157.5 < data['current']['wind_direction_10m'] <= 202.5:
            data['current']['wind_direction_10m'] = 'S'
        elif 202.5 < data['current']['wind_direction_10m'] <= 247.5:
            data['current']['wind_direction_10m'] = 'SW'
        elif 247.5 < data['current']['wind_direction_10m'] <= 292.5:
            data['current']['wind_direction_10m'] = 'W'
        elif 292.5 < data['current']['wind_direction_10m'] <= 337.5:
            data['current']['wind_direction_10m'] = 'NW'

        return data['current']
    
    async def save_to_database(self, weather_data: WeatherData) -> None:
        # Сохранить данные по подключению к бд
        async with self.async_session() as session:
            session.add(weather_data)
            await session.commit()

    async def export_to_excel(self) -> None:
        async with self.async_session() as session:
            # Сделаем запрос всех данных в бд
            query = await session.execute(select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(10))
            export_weather = query.scalars().all()
            # Создадим класс Workbook для работы с excel
            wb = Workbook()
            ws = wb.active
            # Объявим заголовки представления данных в файле
            headers = ['Timestamp', 'Temperature (°C)', 'Wind Speed (m/s)', 'Wind Direction', 'Pressure (mmHg)',
                    'Precipitation Type', 'Precipitation Amount (mm)']
            ws.append(headers)
            for data in export_weather:
                row = [data.timestamp, data.temperature, data.wind_speed, data.wind_direction,
                    data.pressure, data.precipitation_type, data.precipitation_amount]
                ws.append(row)
            # Сохраняем файл 
            wb.save(f'./xlsx_export/data_export_{datetime.now()}.xlsx')

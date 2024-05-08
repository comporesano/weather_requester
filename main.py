import asyncio
from weather_requester import WeatherRequester
from weather_data import WeatherData
from datetime import datetime
from aioconsole import ainput

async def get_user_input(message):
    return await ainput(message)

async def check_command(weather_requester):
    while True:
        export_command = await get_user_input('@Print "export" for export to .xlsx file - ')
        if export_command.strip() == 'export':
            asyncio.create_task(weather_requester.export_to_excel())

async def main():
    wr = WeatherRequester()
    export_task = asyncio.create_task(check_command(wr))
    while True:
        weather_task = asyncio.create_task(wr.request_weather())
        weather = await weather_task
        weather_data = WeatherData(
            timestamp=datetime.now(),
            temperature=weather['temperature_2m'],
            wind_speed=weather['wind_speed_10m'],
            wind_direction=weather['wind_direction_10m'],
            pressure=weather['pressure_msl'],
            precipitation_type=weather['precipitation_type'],
            precipitation_amount=weather['precipitation']
        )
        await wr.save_to_database(weather_data)

        await asyncio.sleep(180)

if __name__ == '__main__':
    asyncio.run(main())

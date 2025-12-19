"""
Модуль для работы с API погоды
"""

import aiohttp
import asyncio
from bot.config import WEATHER_API_KEY

class WeatherAPI:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Иконки для погоды
        self.icons = {
            "ясно": "☀️",
            "облачно": "☁️",
            "пасмурно": "☁️",
            "дождь": "🌧️",
            "ливень": "⛈️",
            "гроза": "⛈️",
            "снег": "❄️",
            "туман": "🌫️",
            "ветер": "💨",
        }
    
    def _get_icon(self, description: str) -> str:
        """Возвращает иконку для погоды"""
        desc_lower = description.lower()
        for key, icon in self.icons.items():
            if key in desc_lower:
                return icon
        return "🌤️"
    
    async def get_current_weather(self, city: str) -> dict:
        """Получает текущую погоду для города"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_weather(data)
                    else:
                        data = await response.json()
                        return {
                            "success": False,
                            "error": data.get('message', 'Неизвестная ошибка')
                        }
                        
        except aiohttp.ClientError as e:
            return {"success": False, "error": f"Ошибка сети: {str(e)}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Таймаут запроса"}
        except Exception as e:
            return {"success": False, "error": f"Неизвестная ошибка: {str(e)}"}
    
    def _format_weather(self, data: dict) -> dict:
        """Форматирует данные о погоде"""
        city = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = round(data['main']['pressure'] * 0.750062)  # в мм рт.ст.
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description']
        icon = self._get_icon(description)
        
        return {
            "success": True,
            "city": city,
            "country": country,
            "temp": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "description": description,
            "icon": icon
        }

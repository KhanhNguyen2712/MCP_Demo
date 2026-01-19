from fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("Weather Demo")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5"

@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get current weather for a city.
    
    Args:
        city: Name of the city (e.g., "Hanoi", "Ho Chi Minh")
    """
    if not API_KEY:
        return "Error: OPENWEATHER_API_KEY not found in environment variables."
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric&lang=vi"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            feels_like = data["main"]["feels_like"]
            wind_speed = data["wind"]["speed"]
            pressure = data["main"]["pressure"]
            visibility = data.get("visibility", "N/A")
            if isinstance(visibility, int):
                visibility = f"{visibility / 1000:.1f} km"

            return (
                f"Thời tiết hiện tại ở {city}:\n"
                f"- Điều kiện: {weather}\n"
                f"- Nhiệt độ: {temp}°C (Cảm giác như: {feels_like}°C)\n"
                f"- Độ ẩm: {humidity}%\n"
                f"- Gió: {wind_speed} m/s\n"
                f"- Áp suất: {pressure} hPa\n"
                f"- Tầm nhìn: {visibility}"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Error: City '{city}' not found."
            return f"Error fetching weather: {e}"
        except Exception as e:
            return f"Error: {str(e)}"

@mcp.tool()
async def get_weather_forecast(city: str) -> str:
    """Get 5-day weather forecast for a city.
    
    Args:
        city: Name of the city
    """
    if not API_KEY:
        return "Error: OPENWEATHER_API_KEY not found in environment variables."
        
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric&lang=vi"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Format forecast (just getting one reading per day for simplicity)
            forecast_text = f"Dự báo 5 ngày cho {city}:\n"
            seen_dates = set()
            
            for item in data['list']:
                dt_txt = item['dt_txt']
                date = dt_txt.split()[0]
                
                if date not in seen_dates:
                    temp = item['main']['temp']
                    humidity = item['main']['humidity']
                    wind = item['wind']['speed']
                    weather = item['weather'][0]['description']
                    forecast_text += f"- {date}: Thời tiết: {weather}, Nhiệt độ: {temp}°C, Độ ẩm: {humidity}%, Gió: {wind}m/s\n"
                    seen_dates.add(date)
                    
                    if len(seen_dates) >= 5:
                        break
            
            return forecast_text
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Error: City '{city}' not found."
            return f"Error fetching forecast: {e}"
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()

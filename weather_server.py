from fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict, Counter

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("Weather Demo")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5"

@mcp.resource("weather://safety-guidelines")
def get_safety_guidelines() -> str:
    """Cung cấp lời khuyên an toàn dựa trên điều kiện thời tiết."""
    return """
    HƯỚNG DẪN AN TOÀN THỜI TIẾT:
    - Trời nắng: Mang theo nước, đội mũ, dùng kem chống nắng.
    - Trời mưa: Mang ô/áo mưa, cẩn thận trơn trượt.
    - Dông sét: Tìm nơi trú ẩn an toàn, tránh xa vật kim loại.
    - Sương mù: Giảm tốc độ khi tham gia giao thông, bật đèn sương mù.
    """

@mcp.prompt("weather-report")
def weather_report_prompt(city: str) -> str:
    """Tạo câu lệnh yêu cầu AI báo cáo thời tiết và tư vấn an toàn."""
    return (
        f"Hãy lấy dữ liệu thời tiết hiện tại cho thành phố {city} bằng tool `get_current_weather`. "
        f"Sau đó, hãy đọc tài liệu an toàn từ resource `weather://safety-guidelines` "
        f"để đưa ra bản tin thời tiết kèm lời khuyên an toàn phù hợp nhất cho người dân."
    )

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
            wind_speed = data["wind"]["speed"] * 3.6
            pressure = data["main"]["pressure"]
            visibility = data.get("visibility", "N/A")
            dt = datetime.fromtimestamp(data["dt"]).strftime('%H:%M:%S %d/%m/%Y')
            if isinstance(visibility, int):
                visibility = f"{visibility / 1000:.1f} km"

            return (
                f"Thời tiết hiện tại ở {city}:\n"
                f"- Điều kiện: {weather}\n"
                f"- Nhiệt độ: {temp}°C (Cảm giác như: {feels_like}°C)\n"
                f"- Độ ẩm: {humidity}%\n"
                f"- Gió: {wind_speed:.2f} km/h\n"
                f"- Áp suất: {pressure} hPa\n"
                f"- Tầm nhìn: {visibility}\n"
                f"- Cập nhật lúc: {dt}"
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
            
            # Format forecast (aggregating data by day)
            forecast_text = f"Dự báo 5 ngày cho {city}:\n"
            daily_data = defaultdict(lambda: {
                "temps": [],
                "humidities": [],
                "winds": [],
                "weathers": []
            })
            
            for item in data['list']:
                dt_txt = item['dt_txt']
                date = dt_txt.split()[0]
                
                daily_data[date]["temps"].append(item['main']['temp'])
                daily_data[date]["humidities"].append(item['main']['humidity'])
                daily_data[date]["winds"].append(item['wind']['speed'])
                daily_data[date]["weathers"].append(item['weather'][0]['description'])

            # Process aggregated data
            count = 0
            for date, stats in daily_data.items():
                if count >= 5:
                    break
                
                max_temp = max(stats["temps"])
                min_temp = min(stats["temps"])
                avg_humidity = sum(stats["humidities"]) / len(stats["humidities"])
                avg_wind = (sum(stats["winds"]) / len(stats["winds"])) * 3.6
                
                # Get most common weather description
                most_common_weather = Counter(stats["weathers"]).most_common(1)[0][0]
                
                forecast_text += (
                    f"- {date}: {most_common_weather.capitalize()}. "
                    f"Nhiệt độ: {min_temp:.1f}-{max_temp:.1f}°C, "
                    f"Độ ẩm TB: {avg_humidity:.0f}%, "
                    f"Gió TB: {avg_wind:.1f} km/h\n"
                )
                count += 1
            
            return forecast_text
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Error: City '{city}' not found."
            return f"Error fetching forecast: {e}"
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()

# Weather MCP Server Demo

Một MCP Server đơn giản sử dụng Python và FastMCP để tra cứu thông tin thời tiết từ OpenWeatherMap.

## Yêu cầu

- Python 3.10+
- OpenWeatherMap API Key (miễn phí)

## Hướng dẫn cài đặt

1. **Cài đặt dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Cấu hình API Key:**
   - Tạo file `.env` từ file mẫu:
     ```bash
     cp .env.example .env
     ```
   - Mở file `.env` và dán API key của bạn vào:
     ```
     OPENWEATHER_API_KEY=your_actual_api_key_here
     ```

## Hướng dẫn chạy

### Cách 1: Test bằng MCP Inspector 

MCP Inspector là công cụ visual giúp test server dễ dàng trên trình duyệt.

1. **Chạy Inspector:**
   Mở terminal tại thư mục project và chạy:

   ```bash
   npx @modelcontextprotocol/inspector python weather_server.py
   ```

   _Lần đầu chạy có thể sẽ cần xác nhận cài đặt gói `npx`._

2. **Sử dụng giao diện Web:**
   - Inspector sẽ tự động mở một đường dẫn (thường là `http://localhost:5173`) trên trình duyệt.
   - Nhìn sang panel bên trái sẽ thấy trạng thái **Connected**.
   - Chọn tab **Tools**.
   - Bạn sẽ thấy danh sách tools: `get_current_weather`, `get_weather_forecast`.
   - Chọn một tool (ví dụ `get_current_weather`), nhập tham số `city` (ví dụ: "Hanoi") vào form.
   - Nhấn nút **Run Tool**.
   - Kết quả trả về từ API sẽ hiện ở khung bên phải (Result).

### Cách 2: Tích hợp với Claude Desktop

Thêm configuration sau vào file `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather-demo": {
      "command": "python",
      "args": ["/path/to/MCP_Demo/weather_server.py"]
    }
  }
}
```

**Lưu ý:** Thay `/path/to/MCP_Demo/weather_server.py` bằng đường dẫn tuyệt đối đến file code của bạn.

## Các Tools có sẵn

1. **`get_current_weather(city)`**: Xem thời tiết hiện tại.
2. **`get_weather_forecast(city)`**: Xem dự báo 5 ngày tới.

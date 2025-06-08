import network
import socket
import time
import ntptime
import urequests
import secrets  # Your secrets.py with WiFi & API info

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected. IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def get_weather():
    try:
        url = (
            "http://api.openweathermap.org/data/2.5/weather?q="
            + secrets.CITY_NAME
            + "&appid="
            + secrets.OWM_API_KEY
            + "&units=metric"
        )
        response = urequests.get(url)
        data = response.json()
        response.close()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        sunrise_ts = data["sys"]["sunrise"]
        sunset_ts = data["sys"]["sunset"]
        timezone_offset = data["timezone"]

        def ts_to_str(ts):
            local = time.localtime(ts + timezone_offset)
            hour = local[3] % 12 or 12
            ampm = "am" if local[3] < 12 else "pm"
            return f"{hour}:{local[4]:02}:{local[5]:02} {ampm}"

        sunrise = ts_to_str(sunrise_ts)
        sunset = ts_to_str(sunset_ts)
        descriptions = " ".join([w["description"] for w in data["weather"]])

        return {
            "temp": round(temp, 1),
            "feels_like": round(feels_like, 1),
            "humidity": humidity,
            "wind": round(wind_speed, 2),
            "sunrise": sunrise,
            "sunset": sunset,
            "description": descriptions,
        }

    except Exception as e:
        print("Failed to get weather:", e)
        return None

def format_time_date():
    timezone_offset = 19800  # UTC+5:30 for IST
    t = time.localtime(time.time() + timezone_offset)
    hour_12 = t[3] % 12 or 12
    am_pm = "AM" if t[3] < 12 else "PM"
    time_str = "{:02}:{:02}:{:02} {}".format(hour_12, t[4], t[5], am_pm)
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    date_str = "{:02}-{}-{:02}, {}".format(
        t[2], months[t[1] - 1], t[0] % 100, days[t[6]]
    )
    return time_str, date_str

def webpage(time_str, date_str, weather):
    if not weather:
        return "<html><body><h1>Error fetching weather</h1></body></html>"

    html = f"""
    <html>
        <head>
            <title>Pico Weather</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="30">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    text-align: center;
                    background: transparent;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                }}
                h1 {{ font-size: 2.5em; margin: 0.2em 0; }}
                h2 {{ font-size: 1.5em; margin: 0.2em 0; color: #666; }}
                p  {{ font-size: 1.1em; margin: 0.5em 0; word-wrap: break-word; }}

                @media (max-width: 400px) {{
                    p {{
                        font-size: 1em;
                        line-height: 1.4em;
                    }}
                    h1 {{
                        font-size: 2em;
                    }}
                    h2 {{
                        font-size: 1.2em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{time_str}</h1>
                <h2>{date_str}</h2>
                <p>{weather['description']}</p>
                <p>🌡️ Temp: {weather['temp']}°C</p>
                <p>🤒 Feels like: {weather['feels_like']}°C</p>
                <p>💧 Humidity: {weather['humidity']}%</p>
                <p>💨 Wind: {weather['wind']} m/s</p>
                <p>🌅 Sunrise: {weather['sunrise']}</p>
                </p>🌇 Sunset: {weather['sunset']}</p>
                
            </div>
        </body>
    </html>
    """
    return html



def main():
    ip = connect_wifi()
    print("Syncing time with NTP...")
    try:
        ntptime.settime()
        print("Time synced!")
    except:
        print("Failed to sync time")

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Listening on http://{}/".format(ip))

    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        try:
            req = cl.recv(1024)
            weather = get_weather()
            time_str, date_str = format_time_date()
            response = webpage(time_str, date_str, weather)
            cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html; charset=utf-8\r\n\r\n")
            cl.send(response)
        except Exception as e:
            print("Error:", e)
        finally:
            cl.close()

main()

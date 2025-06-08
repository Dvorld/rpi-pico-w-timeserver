Step-by-step Guide with Code
Step 1: Prepare Hardware & Software

    Raspberry Pi Pico W

    USB cable to connect Pico W to PC

    Thonny IDE installed on your computer

    MicroPython firmware for Pico W flashed (latest from here)

Step 2: Get OpenWeatherMap API Key

    Go to https://openweathermap.org/api

    Sign up for a free account

    Get your API key from your dashboard (it’s a string like abcdef1234567890abcdef1234567890)

    Note your city name or city ID (we’ll use city name)

Step 3: Connect Pico W to Wi-Fi and test NTP sync
Step 4: Upload the Code to Pico W via Thonny
Step 5: Access the webserver on your phone or laptop
Code Overview

We'll create:

    secrets.py — store Wi-Fi and API info

    main.py — the main program that:

        Connects to Wi-Fi

        Gets NTP time

        Fetches weather info from OpenWeatherMap API

        Runs a simple HTTP server showing time/date/weather

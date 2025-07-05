#!/usr/bin/env python3
"""
Weather MCP Server
Provides weather information and forecasting functionality
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
from mcp.server.fastmcp import FastMCP


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("WeatherService")

# Mock weather data for demonstration
MOCK_WEATHER_DATA = {
    "beijing": {"temp": 22, "humidity": 65, "description": "Partly cloudy"},
    "shanghai": {"temp": 26, "humidity": 70, "description": "Sunny"},
    "guangzhou": {"temp": 28, "humidity": 75, "description": "Partly cloudy"},
    "shenzhen": {"temp": 27, "humidity": 73, "description": "Clear"},
    "hangzhou": {"temp": 24, "humidity": 68, "description": "Overcast"}
}

@mcp.tool()
async def get_current_weather(location: str, units: str = "metric") -> dict:
    """
    Get current weather information for a specified location
    
    Args:
        location: City name or location identifier
        units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
    
    Returns:
        dict: Current weather information including temperature, humidity, and conditions
    """
    logger.info(f"Getting current weather for {location} in {units} units")
    
    # Normalize location name
    location_key = location.lower().replace(" ", "")
    
    # Get base weather data (mock or from API)
    if location_key in MOCK_WEATHER_DATA:
        base_data = MOCK_WEATHER_DATA[location_key].copy()
    else:
        # Generate random weather data for unknown locations
        base_data = {
            "temp": random.randint(15, 30),
            "humidity": random.randint(40, 80),
            "description": random.choice(["Sunny", "Partly cloudy", "Overcast", "Light rain"])
        }
    
    # Convert temperature if needed
    temperature = base_data["temp"]
    if units == "imperial":
        temperature = round(temperature * 9/5 + 32, 1)
    
    # Add some realistic variations
    feels_like = temperature + random.randint(-3, 3)
    wind_speed = round(random.uniform(2, 15), 1)
    pressure = random.randint(980, 1030)
    
    result = {
        "location": location,
        "temperature": temperature,
        "feels_like": feels_like,
        "humidity": base_data["humidity"],
        "pressure": pressure,
        "wind_speed": wind_speed,
        "description": base_data["description"],
        "units": units,
        "timestamp": datetime.now().isoformat(),
        "source": "mock_weather_service"
    }
    
    logger.info(f"Weather data for {location}: {temperature}°{'C' if units == 'metric' else 'F'}, {base_data['description']}")
    return result

@mcp.tool()
async def get_weather_forecast(location: str, days: int = 3, units: str = "metric") -> dict:
    """
    Get weather forecast for a specified location
    
    Args:
        location: City name or location identifier
        days: Number of days to forecast (1-7)
        units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
    
    Returns:
        dict: Weather forecast data for the specified number of days
    """
    logger.info(f"Getting {days}-day weather forecast for {location}")
    
    # Validate days parameter
    days = max(1, min(days, 7))
    
    # Get current weather as base
    current = await get_current_weather(location, units)
    base_temp = current["temperature"]
    
    forecast = []
    weather_conditions = ["Sunny", "Partly cloudy", "Overcast", "Light rain", "Heavy rain", "Thunderstorms"]
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        
        # Generate realistic temperature variations
        temp_variation = random.randint(-5, 5)
        high_temp = base_temp + temp_variation + random.randint(2, 8)
        low_temp = base_temp + temp_variation - random.randint(2, 8)
        
        forecast_day = {
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": date.strftime("%A"),
            "high_temperature": round(high_temp, 1),
            "low_temperature": round(low_temp, 1),
            "description": random.choice(weather_conditions),
            "precipitation_chance": f"{random.randint(0, 100)}%",
            "humidity": random.randint(40, 85),
            "wind_speed": round(random.uniform(3, 20), 1)
        }
        
        forecast.append(forecast_day)
    
    result = {
        "location": location,
        "forecast_days": days,
        "units": units,
        "forecast": forecast,
        "timestamp": datetime.now().isoformat(),
        "source": "mock_weather_service"
    }
    
    logger.info(f"Generated {days}-day forecast for {location}")
    return result

@mcp.tool()
async def get_weather_alerts(location: str) -> dict:
    """
    Get weather alerts and warnings for a specified location
    
    Args:
        location: City name or location identifier
    
    Returns:
        dict: Weather alerts and warnings information
    """
    logger.info(f"Getting weather alerts for {location}")
    
    # Generate mock alerts (in real implementation, this would come from weather API)
    alerts = []
    
    # Randomly generate some alerts for demonstration
    alert_types = [
        ("Heat Warning", "High temperatures expected", "high"),
        ("Rain Advisory", "Moderate rainfall expected", "medium"),
        ("Wind Alert", "Strong winds forecasted", "medium"),
        ("Air Quality", "Moderate air pollution levels", "low"),
        ("UV Index", "High UV radiation levels", "medium")
    ]
    
    # Generate 0-3 random alerts
    num_alerts = random.randint(0, 3)
    for i in range(num_alerts):
        alert_type, description, severity = random.choice(alert_types)
        
        start_time = datetime.now() + timedelta(hours=random.randint(1, 24))
        end_time = start_time + timedelta(hours=random.randint(2, 48))
        
        alert = {
            "id": f"alert_{i+1}_{int(datetime.now().timestamp())}",
            "type": alert_type,
            "severity": severity,
            "title": f"{alert_type} for {location}",
            "description": description,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "issued_by": "Weather Service"
        }
        
        alerts.append(alert)
    
    result = {
        "location": location,
        "alert_count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.now().isoformat(),
        "source": "mock_weather_service"
    }
    
    logger.info(f"Found {len(alerts)} weather alerts for {location}")
    return result

@mcp.tool()
async def get_air_quality(location: str) -> dict:
    """
    Get air quality information for a specified location
    
    Args:
        location: City name or location identifier
    
    Returns:
        dict: Air quality index and pollutant information
    """
    logger.info(f"Getting air quality for {location}")
    
    # Generate mock air quality data
    aqi = random.randint(20, 200)
    
    # Determine air quality level based on AQI
    if aqi <= 50:
        level = "Good"
        color = "green"
    elif aqi <= 100:
        level = "Moderate"
        color = "yellow"
    elif aqi <= 150:
        level = "Unhealthy for Sensitive Groups"
        color = "orange"
    elif aqi <= 200:
        level = "Unhealthy"
        color = "red"
    else:
        level = "Very Unhealthy"
        color = "purple"
    
    pollutants = {
        "pm25": random.randint(10, 80),
        "pm10": random.randint(20, 120),
        "o3": random.randint(30, 150),
        "no2": random.randint(10, 100),
        "so2": random.randint(5, 50),
        "co": round(random.uniform(0.5, 5.0), 1)
    }
    
    result = {
        "location": location,
        "aqi": aqi,
        "level": level,
        "color": color,
        "pollutants": pollutants,
        "health_recommendations": {
            "general": f"Air quality is {level.lower()}",
            "sensitive": "Sensitive individuals should limit outdoor activities" if aqi > 100 else "No special precautions needed"
        },
        "timestamp": datetime.now().isoformat(),
        "source": "mock_weather_service"
    }
    
    logger.info(f"Air quality for {location}: AQI {aqi} ({level})")
    return result

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp.run(transport="stdio")
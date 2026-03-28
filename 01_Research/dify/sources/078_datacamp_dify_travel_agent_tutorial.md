---
source_id: "078"
title: "Dify: A Guide With Demo Project (DataCamp)"
url: "https://www.datacamp.com/tutorial/dify"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify chatbot tutorial", "Dify workflow tutorial", "Dify use cases"]
content_length: 8950
---

# Dify: A Guide With Demo Project

Author: Francois Aubry, DataCamp

## What Is Dify?

Dify is a platform designed to simplify the development of AI applications without requiring extensive coding skills. It provides a user-friendly, low-code environment where users can build apps by dragging and dropping different components.

Each type of block has inputs and transforms these into different outputs, depending on the block type. Information is passed around and transformed from block to block, producing the final result.

## Getting Started With Dify

Two ways of using Dify:
- Local setup (Docker)
- Cloud version (free plan available)

## Creating a Chatflow With Dify

Dify provides several types of apps. A Chatflow app is an AI flow where users use a chat interface to interact with the agent.

### Default Flow

The default flow has three blocks:
- The **Start** block starts the flow (triggered by user message in Chatflow)
- The **LLM** node takes user message input and sends it to an LLM (e.g., gpt-4)
- The **Final** node displays a message in the chat

### Installing and Setting Up the OpenAI Plugin

Steps: Click Plugins > Install from Marketplace > Search "openai" > Install. Then configure API key via LLM node > configuration icon > Model Provider Settings > Setup > paste API key.

### Creating Variables

Dify makes it possible to store application state by assigning values to variables accessible to all blocks. Create variables via the variable button (e.g., a "name" variable storing a string).

### IF/ELSE Blocks

IF/ELSE blocks check variable values to control flow. Connect different Answer blocks to IF (condition true) and ELSE (condition false) outputs.

### Variable Assigner and Parameter Extractor Blocks

The **Parameter Extractor** block uses an LLM to extract information from conversation. Configuration includes:
- INPUT VARIABLE: sys.query (user message)
- EXTRACTION PARAMETERS: define information to extract
- INSTRUCTION: prompt to guide LLM

The **Variable Assigner** block assigns extracted values to variables.

### Code Block

Code blocks execute custom Python code. Example: making requests to OpenWeather API for weather forecasts based on extracted location.

```python
import requests
API_KEY = "YOUR_KEY"
def main(location: str) -> str:
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": API_KEY, "units": "metric"}
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return {"result": f"Current weather in {location}: {weather_desc}, Temperature: {temp} C"}
    else:
        return {"result": "Could not retrieve weather data"}
```

## Project: Creating a Travel Planner AI Agent

The agent plans a single day of a trip by gathering user's location and preferred activities.

Variables: `location` (string) and `activities` (array of strings).

Flow design:
1. Variable extraction block extracts both location and activities from user messages
2. IF/ELSE blocks check whether each parameter was extracted
3. Variable Assigner updates values
4. Another IF/ELSE checks for missing values; asks user if something is missing
5. Code block fetches weather via API
6. LLM block receives weather, location, and activities to plan the day

The LLM block uses a system prompt injected with location, activities, and weather variables.

### Conversation Opener

Enable the Conversation Opener feature to display a greeting message when chat starts.

## Dify Tools

Tools are powerful extensions that allow AI agents to interact with the outside world. While an LLM can reason and generate responses, it doesn't have real-time access to live data or external services.

Tools solve this by enabling API calls, querying databases, performing calculations, retrieving documents, and more. Configure tools through the visual interface by specifying tool type, input/output schema, and authentication requirements.

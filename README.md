# Assignment01 API

## Project structure

```text
src/
├── main.py                   # FastAPI app, lifespan logging, exception handler, root and /health
├── config.py                 # Loads settings and environment variables from src/.env
├── logging_config.py         # Configures rotating file and console logging
├── auth/
│   └── dependencies.py       # Validates the X-API-Key header
├── joke/
│   ├── router.py             # /joke endpoint
│   ├── client.py             # Calls the external Joke API
│   └── schema.py             # JokeResponse model
├── weather/
│   ├── router.py             # /weather endpoint
│   ├── client.py             # Calls the OpenWeather API
│   └── schema.py             # WeatherResponse model
└── summary/
    ├── router.py             # API-key protected /summary endpoint
    ├── client.py             # LangGraph workflow using ChatAnthropic
    └── schema.py             # SummaryRequest and SummaryResponse models
```

## Endpoints

- **`GET /joke`** - Fetches a random joke from the external Joke API and returns `joke` and `category`. Upstream failures return `502`.
- **`GET /weather?city=<city>`** - Fetches current weather from OpenWeather and returns `city`, `temperature`, `condition`, and `humidity`. Unknown cities return `404`; upstream failures return `502`.
- **`POST /summary`** - Requires the `X-API-Key` header and accepts `{"text": "..."}`. It validates the text length, runs the LLM workflow, and returns `{"summary": "..."}`. Missing or invalid keys return `401`; invalid text returns `400`; LLM failures return `502`.
- **`GET /health`** - Returns `{"status": "ok"}` when the app is responding.

## Summary (LLM)

The `/summary` endpoint uses **LangGraph** to run a summarization node. The node uses LangChain's **`ChatAnthropic`** integration to call Claude through the Anthropic API. This uses an external LLM API; it does not use Ollama locally. Configure an Anthropic API key and a model available to that key.

## Logs

Application logs are written to `logs/app.log`, and are also printed to the console. The log directory and file are created automatically when the app starts.

```powershell
Get-Content .\logs\app.log -Tail 30
```

## Setup

Run these commands from the project root:

```powershell
py -3.13 -m pip install -r requirements.txt
New-Item -ItemType Directory -Force src | Out-Null
notepad src\.env
```

Add your own values to `src\.env`:

```dotenv
OPENWEATHER_API_KEY=your-weather-key
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
JOKE_API_BASE_URL=https://v2.jokeapi.dev
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-sonnet-4-6
APP_API_KEY=your-private-api-key
MAX_SUMMARY_TEXT_LENGTH=5000
```

Do not commit `src/.env` or share its secret values. The `APP_API_KEY` is the private key clients must send in the `X-API-Key` header; it is separate from the Anthropic key.

## Run the application

Start the server from the project root:

```powershell
py -3.13 -m uvicorn src.main:app --reload
```

Swagger UI: <http://127.0.0.1:8000/docs>

Example summary request body:

```json
{
  "text": "Solar energy converts sunlight into electricity and can reduce reliance on fossil fuels."
}
```

Include the `X-API-Key` header with the value configured as `APP_API_KEY` in `src/.env`.

## Run tests

Tests use an isolated test API key and replace the external endpoint calls where needed, so they do not require live weather, joke, or Claude API requests.

```powershell
py -3.13 -m pytest -v
```

Run the command from the project root.


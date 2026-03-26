# Yellow.ai Assignment 2

Python solution for the weather-aware order delay checker.

## What this project does

- Reads orders from `orders.json`
- Fetches current weather for each city concurrently using `asyncio.gather`
- Marks orders as `Delayed` when the weather `main` status is `Rain`, `Snow`, or `Extreme`
- Generates a personalized apology message for delayed orders
- Handles invalid cities without crashing the script
- Loads the API key from `.env` instead of hardcoding it

## Project files

- `main.py`: main assignment script
- `orders.json`: local order database provided in the assignment
- `.env.example`: example environment file
- `ai_log.md`: prompts used while building the solution

## Setup

1. Create a free API key from OpenWeatherMap.
2. Copy `.env.example` to `.env`.
3. Replace the placeholder value with your real API key.

## Run

```bash
python main.py
```

## Expected behavior

- Valid cities are processed in parallel
- Orders with bad weather are updated to `Delayed`
- A personalized apology message is added to delayed orders
- Invalid cities are reported in the console and do not stop the program
- `orders.json` is updated in place after processing

## Notes for submission

- Run the script once with your real API key before submitting so `orders.json` contains the latest updated statuses.
- Add your GitHub repo link, demo recording link, and workflow/bot access link if required by the form.

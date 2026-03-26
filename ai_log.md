# AI Log

## Prompt 1: Parallel Fetching

Create a Python solution for a weather-based order processor that reads orders from `orders.json`, fetches current weather for each city concurrently using `asyncio.gather`, and updates the order status to `Delayed` when the weather `main` value is `Rain`, `Snow`, or `Extreme`.

## Prompt 2: Error Handling

Add resilient error handling so an invalid city like `InvalidCity123` is logged clearly, but the script continues processing the remaining valid cities without crashing.

## Prompt 3: Personalized Apology

Write a Python function that generates a short weather-aware apology message such as: `Hi Alice, your order to New York is delayed due to heavy rain. We appreciate your patience!`

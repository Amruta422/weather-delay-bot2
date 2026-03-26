import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_DIR = Path(__file__).resolve().parent
ORDERS_PATH = BASE_DIR / "orders.json"
ENV_PATH = BASE_DIR / ".env"
DELAY_WEATHER_TYPES = {"Rain", "Snow", "Extreme"}
API_URL = "https://api.openweathermap.org/data/2.5/weather"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_orders(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("orders.json must contain a list of orders.")

    return data


def save_orders(path: Path, orders: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(orders, file, indent=2)
        file.write("\n")


def generate_weather_aware_apology(
    customer_name: str, city: str, weather_main: str, weather_description: str
) -> str:
    reason = weather_description.strip() or weather_main.lower()
    return (
        f"Hi {customer_name}, your order to {city} is delayed due to {reason}. "
        "We appreciate your patience!"
    )


def fetch_weather(city: str, api_key: str) -> Dict[str, Any]:
    query = urlencode({"q": city, "appid": api_key, "units": "metric"})
    request_url = f"{API_URL}?{query}"

    try:
        with urlopen(request_url, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {error.code} while fetching weather for '{city}': {details}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Network error while fetching weather for '{city}': {error.reason}"
        ) from error


async def fetch_weather_async(city: str, api_key: str) -> Dict[str, Any]:
    return await asyncio.to_thread(fetch_weather, city, api_key)


def extract_weather_fields(payload: Dict[str, Any]) -> Tuple[str, str]:
    weather_items = payload.get("weather")
    if not isinstance(weather_items, list) or not weather_items:
        raise ValueError("Weather payload does not contain a valid 'weather' list.")

    first_item = weather_items[0]
    if not isinstance(first_item, dict):
        raise ValueError("Weather payload contains an invalid weather item.")

    weather_main = str(first_item.get("main", "")).strip()
    weather_description = str(first_item.get("description", "")).strip()

    if not weather_main:
        raise ValueError("Weather payload is missing the main weather status.")

    return weather_main, weather_description


async def process_order(
    order: Dict[str, Any], api_key: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    order_id = str(order.get("order_id", "unknown"))
    customer = str(order.get("customer", "Customer"))
    city = str(order.get("city", "")).strip()

    if not city:
        return None, f"Order {order_id}: city is missing."

    try:
        payload = await fetch_weather_async(city, api_key)
        weather_main, weather_description = extract_weather_fields(payload)
    except Exception as error:
        return None, f"Order {order_id} ({city}): {error}"

    order["weather_main"] = weather_main
    order["weather_description"] = weather_description

    if weather_main in DELAY_WEATHER_TYPES:
        order["status"] = "Delayed"
        order["apology_message"] = generate_weather_aware_apology(
            customer, city, weather_main, weather_description
        )
    else:
        order["status"] = "On Time"
        order.pop("apology_message", None)

    return order, None


async def process_orders(orders: List[Dict[str, Any]], api_key: str) -> List[str]:
    tasks = [process_order(order, api_key) for order in orders]
    results = await asyncio.gather(*tasks)

    errors: List[str] = []
    for _, error in results:
        if error:
            errors.append(error)

    return errors


async def async_main() -> int:
    load_env_file(ENV_PATH)
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()

    if not api_key:
        print(
            "Missing OPENWEATHER_API_KEY. Add it to a .env file or your environment.",
            file=sys.stderr,
        )
        return 1

    if not ORDERS_PATH.exists():
        print("orders.json was not found in the project folder.", file=sys.stderr)
        return 1

    try:
        orders = load_orders(ORDERS_PATH)
    except Exception as error:
        print(f"Failed to read orders.json: {error}", file=sys.stderr)
        return 1

    errors = await process_orders(orders, api_key)
    save_orders(ORDERS_PATH, orders)

    delayed_orders = [order for order in orders if order.get("status") == "Delayed"]

    print(f"Processed {len(orders)} orders.")
    print(f"Delayed orders: {len(delayed_orders)}")

    if delayed_orders:
        print("\nGenerated apology messages:")
        for order in delayed_orders:
            print(f"- {order['order_id']}: {order['apology_message']}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))

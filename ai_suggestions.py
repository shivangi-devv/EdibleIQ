
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_recipe_suggestions(food_items):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "API key not found. Please check your .env file."

    if not food_items:
        return "Please add food items to your inventory first."

    client = genai.Client(api_key=api_key)

    food_list = ""

    for item in food_items:
        food_list += (
            f'{item["name"]} - '
            f'{item["quantity"]} {item["unit"]}, '
            f'Category: {item["category"]}, '
            f'Expiry: {item["expiry_date"]}\n'
        )

    prompt = f"""
    You are an expert food recipe assistant.

    Suggest 3 easy recipes using these ingredients:

    {food_list}

    IMPORTANT:
    - Prioritize ingredients expiring soon.
    - Give recipe names.
    - List ingredients and quantities.
    - Explain cooking steps simply.
    - Include preparation time.
    - Keep recipes beginner-friendly.
    """

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            if response.text:
                return response.text

            return "Gemini returned an empty response. Please try again."

        except Exception as e:

            error = str(e).upper()

            if (
                ("503" in error or "UNAVAILABLE" in error)
                and attempt < 2
            ):

                time.sleep(3 * (attempt + 1))
                continue

            return (
                "AI service is temporarily busy. "
                "Please try again in a few minutes.\n\n"
                f"Technical details: {e}"
            )


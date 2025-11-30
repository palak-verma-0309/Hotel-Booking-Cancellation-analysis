import requests

MODEL = "meta-llama/Llama-3.2-1B-Instruct"

def get_retention_strategy(api_key, booking_details):
    if not api_key:
        return "Error: Token Missing in Sidebar."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"The customer might cancel their hotel booking.\n"
        f"- Market Segment: {booking_details['market_segment']}\n"
        f"- Lead Time: {booking_details['lead_time']} days\n"
        f"- Country: {booking_details['country']}\n"
        f"Give one short reason for cancellation and one helpful retention offer."
    )

    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150
            }
        )

        print("DEBUG:", response.status_code, response.text)

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        if response.status_code == 401:
            return "Error: Invalid Token"

        return "AI Service Busy. Suggestion: Offer a Free Room Upgrade."

    except Exception as e:
        print("EXCEPTION:", e)
        return "AI Service Busy. Suggestion: Offer a Free Room Upgrade."

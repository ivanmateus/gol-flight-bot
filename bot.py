import requests
import os
import json

URL = "https://vg-api.airtrfx.com/graphql"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("Bot started")

def send_telegram(msg):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing", TELEGRAM_TOKEN, CHAT_ID)
        return

    print("Sending telegram message...")
    print(msg)

    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

    print("Telegram response:")
    print(r.text)


payload = [
{
"operationName": "GetStandardFareModule",
"variables": {
"page": {
"tenant": "g3",
"slug": "voos",
"siteEdition": "br"
},
"id": "64a711119ee59abba30be731",
"pageNumber": 1,
"limit": 20,
"flatContext": {
"templateId": "64a5c38850ebd9da02000012",
"templateName": "home"
},
"filters": {
"budget": {
"max": 600
},
"origin": {
"code": "SAO",
"geoId": "-3461786"
},
"destination": {
"code": "MAO",
"geoId": "6300620"
}
},
"urlParameters": {},
"nearestOriginAirport": {}
},
"query": """query GetStandardFareModule($page: PageInput!, $id: String!, $pageNumber: Int, $limit: Int, $flatContext: FlatContextInput, $urlParameters: StandardFareModuleUrlParameters, $filters: StandardFareModuleFiltersInput, $nearestOriginAirport: AirportInput) {
standardFareModule(page: $page, id: $id, pageNumber: $pageNumber, limit: $limit, flatContext: $flatContext, urlParameters: $urlParameters, filters: $filters, nearestOriginAirport: $nearestOriginAirport) {
fares(pageNumber: $pageNumber, limit: $limit) {
originCity
destinationCity
formattedDepartureDate
formattedTotalPrice
priceLastSeen {
value
unit
}
}
}
}
"""
}
]


def run():

    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }

    print("Sending request to API...")

    r = requests.post(URL, json=payload, headers=headers)

    print("Status code:", r.status_code)

    data = r.json()

    print("Raw response:")
    print(json.dumps(data, indent=2))

    fares = data[0]["data"]["standardFareModule"]["fares"]

    print("Number of fares received:", len(fares))

    for fare in fares:

        seen = fare["priceLastSeen"]
        value = int(seen["value"])
        unit = seen["unit"]

        print("Checking fare:")
        print(fare)

        recent = False

        if unit == "minute" or unit == "minutes":
            recent = True

        if (unit == "hour" or unit == "hours") and value < 24:
            recent = True

        if recent:

            message = (
                "⚠ Recent Fare Found\n\n"
                f"{fare['originCity']} → {fare['destinationCity']}\n"
                f"Departure: {fare['formattedDepartureDate']}\n"
                f"Price: {fare['formattedTotalPrice']}\n\n"
                f"Seen {value} {unit.lower()} ago"
            )

            send_telegram(message)


if __name__ == "__main__":
    run()

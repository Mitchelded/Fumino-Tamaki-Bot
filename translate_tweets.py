import requests


def translate_language(sl, dl, text):
    url = "https://ftapi.pythonanywhere.com/translate"
    params = {
        "sl": f"{sl}",  # Source language is Japanese
        "dl": f"{dl}",  # Destination language is English
        "text": f"{text}"  # Text to be translated (means "hello" in Japanese)
    }

    response = requests.get(url, params=params)
    return response.json()["destination-text"]

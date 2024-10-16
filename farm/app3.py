import requests
from flask import Flask, request
import africastalking
import os
import google.generativeai as genai

app = Flask(__name__)

# Africa's Talking Credentials
username = "atsk_540abf0e247c0d7d9718250124230967b03fd71d8752a5ab53d149f4812e67eccbbdb8f5"
api_key = "Sandbox"  # Replace with your Africa's Talking API key
africastalking.initialize(username, api_key)

# OpenWeather API key
open_weather_api_key = "f5ed74e65749468fae4833a12d7e01ba"

# Initialize Google Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define regions and their counties with coordinates (latitude, longitude) for OpenWeather
regions_coordinates = {
    "Nairobi": {"lat": -1.2921, "lon": 36.8219},
    "Coast": {"lat": -4.0435, "lon": 39.6682},
    "Central": {"lat": -0.4167, "lon": 37.0738},
    "Rift Valley": {"lat": 0.5143, "lon": 35.2698},
    "Western": {"lat": 0.2833, "lon": 34.7500},
    "Nyanza": {"lat": -0.0917, "lon": 34.7675},
    "Eastern": {"lat": 0.0510, "lon": 37.6475},
    "North Eastern": {"lat": 3.9373, "lon": 41.8569}
}

# Google Gemini configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

def gemini_nlp(text, language="en"):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"{text} in {language}")
    return response.text

@app.route('/')
def home():
    return "Welcome to the Agriculture Information System for Kenyan Farmers!"

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get('sessionId')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text')

    response = handle_ussd(text, phone_number)

    return response

def handle_ussd(text, phone_number):
    # Split the input text using '*' to track the USSD flow
    split_text = text.split('*')
    
    # If no language is selected, present the language options
    if len(split_text) == 1 and split_text[0] == '':  # Initial menu
        return "CON Welcome! Please choose a language: \n1. Kiswahili \n2. English \n3. Kikuyu \n4. Luo \n5. Kalenjin"

    # Step 1: Language selection
    language_choice = split_text[0]
    language = None

    if language_choice == "1":
        language = "sw"
    elif language_choice == "2":
        language = "en"
    elif language_choice == "3":
        language = "kikuyu"
    elif language_choice == "4":
        language = "luo"
    elif language_choice == "5":
        language = "kalenjin"
    else:
        return "END Invalid language choice. Please try again."

    # Step 2: Region selection after the language is chosen
    if len(split_text) == 1:
        return {
            "sw": "CON Tafadhali chagua eneo: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern",
            "en": "CON Please select a region: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern",
            "kikuyu": "CON Thagũ chagua mũndũ wa tene: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern",
            "luo": "CON Par yie uru gik ma en yien: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern",
            "kalenjin": "CON Aeng' chito ne: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"
        }[language]
    
    # Step 3: Region selection and prompt for information
    if len(split_text) == 2:
        selected_region = split_text[1]
        try:
            selected_region = int(selected_region)
        except ValueError:
            return "END Invalid region selection. Please try again."

        if selected_region >= 1 and selected_region <= 8:
            region_name = list(regions_coordinates.keys())[selected_region - 1]
            return {
                "sw": f"CON Umechagua {region_name}. Je, unahitaji habari gani?\n1. Hali ya Hewa\n2. Bei za Soko\n3. Udhibiti wa Wadudu na Magonjwa\n4. Uliza Swali",
                "kikuyu": f"CON Mũnoine {region_name}. Gweterera ũgũrũrũ o mũndũ:\n1. Hewa\n2. Bei cia Ndũka\n3. Kũheo wega kwa ũrathi na tiini\n4. Rũgũrũ ria Mũtĩri",
                "luo": f"CON Isechuo {region_name}. Inyalo yudo neno nini?\n1. Weche mag Yamo\n2. Yien mar Soko\n3. Luo kendo Yomagi\n4. Penjo Penjo",
                "kalenjin": f"CON Koua {region_name}. Meleele chei itinye kebenya?\n1. Kaletab Ing'o\n2. Ibutab Neing'o\n3. Chepnget ne Setyo\n4. Penya Penya",
                "en": f"CON You have selected {region_name}. What information do you need?\n1. Weather\n2. Market Prices\n3. Pest and Disease Control\n4. Ask a Question"
            }[language]

    return "END Invalid choice. Please try again."



def get_weather_for_region(region_name):
    """
    Fetches the current weather from OpenWeather API for the given region.
    :param region_name: Name of the selected region.
    :return: Formatted weather information string.
    """
    coordinates = regions_coordinates[region_name]
    lat = coordinates['lat']
    lon = coordinates['lon']

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The current weather in {region_name} is {weather} with a temperature of {temperature}°C."
    else:
        return "Unable to fetch the weather information at the moment."

if __name__ == '__main__':
    app.run(debug=True)

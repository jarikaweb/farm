import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import africastalking
import os
import google.generativeai as genai

app = Flask(__name__)

# Africa's Talking Credentials
username = "atsk_540abf0e247c0d7d9718250124230967b03fd71d8752a5ab53d149f4812e67eccbbdb8f5"
api_key = "Sandbox"  # Replace with your Africa's Talking API key
africastalking.initialize(username, api_key)

# Initialize Google Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define regions and their counties for web scraping
regions = {
    "Nairobi": "Nairobi",
    "Coast": "Coast",
    "Central": "Central",
    "Rift Valley": "Rift-Valley",
    "Western": "Western",
    "Nyanza": "Nyanza",
    "Eastern": "Eastern",
    "North Eastern": "North-Eastern"
}

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
    language = "en"
    
    if text == "":
        return "CON Welcome! Please choose a language: \n1. Kiswahili \n2. English \n3. Kikuyu \n4. Luo \n5. Kalenjin"

    if text in ["1", "2", "3", "4", "5"]:
        language = {"1": "sw", "2": "en", "3": "kikuyu", "4": "luo", "5": "kalenjin"}[text]
        return "CON Tafadhali chagua eneo: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"

    split_text = text.split('*')
    
    if len(split_text) == 2:
        selected_region = split_text[1]
        try:
            selected_region = int(selected_region)
        except ValueError:
            return "END Invalid region selection. Please try again."

        if selected_region >= 1 and selected_region <= 8:
            region_name = list(regions.keys())[selected_region - 1]
            return f"CON Umechagua {region_name}. Je, unahitaji habari gani?\n1. Hali ya Hewa\n2. Bei za Soko\n3. Kudhibiti Wadudu na Magonjwa\n4. Uliza Swali"
        else:
            return "END Invalid region selection. Please try again."

    if text.startswith("1*"):  # Weather option selected
        selected_option = split_text[1]
        region_name = list(regions.keys())[int(selected_option) - 1]
        weather_info = fetch_weather_online(region_name)
        return f"END {weather_info}"

    return "END Invalid choice. Please try again."

def fetch_weather_online(region_name):
    """
    Fetches the current weather from an online source.
    :param region_name: Name of the selected region.
    :return: Formatted weather information string.
    """
    try:
        # URL to fetch weather data (modify according to the actual website)
        url = f"https://www.weather.com/weather/today/l/{regions[region_name]}"

        # Sending a request to the website
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the data (adjust selectors according to the website structure)
        temperature = soup.find('span', class_='CurrentConditions--tempValue--3a50n').text
        weather = soup.find('div', class_='CurrentConditions--phraseValue--2xXSr').text
        
        return f"The current weather in {region_name} is {weather} with a temperature of {temperature}."
    except Exception as e:
        return "Unable to fetch the weather information at the moment."

if __name__ == '__main__':
    app.run(debug=True)

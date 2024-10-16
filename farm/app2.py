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
genai.configure(api_key=os.environ["GEMINI_API_KEY"])  # Ensure GEMINI_API_KEY is set in environment variables

# Define regions and their counties
regions_counties = {
    "Nairobi": ["Nairobi City"],
    "Coast": ["Mombasa", "Kilifi", "Kwale", "Lamu"],
    "Central": ["Nyeri", "Murang'a", "Kiambu", "Kirinyaga"],
    "Rift Valley": ["Nakuru", "Uasin Gishu", "Bomet"],
    "Western": ["Kakamega", "Bungoma", "Vihiga"],
    "Nyanza": ["Kisumu", "Homa Bay", "Migori"],
    "Eastern": ["Meru", "Embu", "Kitui"],
    "North Eastern": ["Garissa", "Wajir", "Mandera"]
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
    """
    Function to send the user's text to Google Gemini API for processing.
    :param text: The text to be processed.
    :param language: The language to use.
    :return: Processed text from Gemini API.
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )
    
    chat_session = model.start_chat(
        history=[]
    )
    
    # Send the text to the model for a response
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

    # Process the USSD text with language selection
    response = handle_ussd(text, phone_number)

    return response

def handle_ussd(text, phone_number):
    """
    Handles the USSD logic and uses Google Gemini API for NLP.
    :param text: USSD input text.
    :param phone_number: The phone number of the user for messaging if needed.
    :return: USSD response.
    """
    if text == "":
        return "CON Welcome! Please choose a language: \n1. Kiswahili \n2. English \n3. Kikuyu \n4. Luo \n5. Kalenjin"

    # Handle language selection
    language = "en"  # Default language is English
    if text == "1":
        language = "sw"
        return "CON Tafadhali chagua eneo: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"
    elif text == "2":
        return "CON Please select a region: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"
    elif text == "3":
        language = "kikuyu"
        return "CON Thagũ chagua mũndũ wa tene: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"
    elif text == "4":
        language = "luo"
        return "CON Par yie uru gik ma en yien: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"
    elif text == "5":
        language = "kalenjin"
        return "CON Aeng' chito ne: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"

    # Handle region selection based on language
    if text.startswith("1*") or text.startswith("2*") or text.startswith("3*") or text.startswith("4*") or text.startswith("5*"):
        selected_region = text.split('*')[1]
        region_name = list(regions_counties.keys())[int(selected_region) - 1]
        counties = regions_counties[region_name]

        # Display the main menu
        return f"CON You have selected {region_name}. What information do you need?\n1. Weather\n2. Market Prices\n3. Pest and Diseases Control\n4. Ask a Question"

    # Handle main menu options
    if text == "1*1":  # Weather
        return "END Current weather information will be fetched soon."

    elif text == "1*2":  # Market Prices
        return "END Latest market prices will be fetched soon."

    elif text == "1*3":  # Pest and Diseases Control
        return "END Pest and diseases control information will be fetched soon."

    elif text == "1*4":  # Ask a Question
        return "CON Please type your question related to farming:"

    # Handle farming-related questions
    if text.startswith("1*4*"):
        user_question = text.split('*', 2)[-1]
        gemini_response = gemini_nlp(user_question, language)

        # If Gemini cannot answer, send a message to the farmer
        if "I don't know" in gemini_response or gemini_response.strip() == "":
            africastalking.SMS.send("Sorry, we cannot answer that right now. We will get back to you shortly.", [phone_number])
            return "END Your question has been received. We will get back to you shortly."
        else:
            return f"END {gemini_response}"

    return "END Invalid choice. Please try again."

if __name__ == '__main__':
    app.run(debug=True)

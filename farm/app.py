from flask import Flask, request, jsonify
import africastalking

app = Flask(__name__)  # Corrected to use __name__

# Africa's Talking Credentials
username = "atsk_540abf0e247c0d7d9718250124230967b03fd71d8752a5ab53d149f4812e67eccbbdb8f5"  # Replace with your Africa's Talking username
api_key = "Sandbox"  # Replace with your Africa's Talking API key

africastalking.initialize(username, api_key)

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

@app.route('/')
def home():
    return "Welcome to the Agriculture Information System for Kenyan Farmers!"

@app.route('/ussd', methods=['POST'])
def ussd():
    # Extract information from the USSD request
    session_id = request.form.get('sessionId')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text')

    # Handle USSD menu logic
    response = handle_ussd(text)
    
    return response

def handle_ussd(text):
    # Default to Kiswahili
    if text == "":
        return "CON Karibu! Tafadhali chagua lugha: \n1. Kiswahili \n2. English"
    
    elif text == "1":
        return "CON Tafadhali chagua eneo: \n1. Nairobi \n2. Coast \n3. Central \n4. Rift Valley \n5. Western \n6. Nyanza \n7. Eastern \n8. North Eastern"

    # Handle region selection
    elif text == "1*1":
        return "CON Umechagua Nairobi. Tafadhali chagua kaunti:\n1. Nairobi City"
    elif text == "1*2":
        return "CON Umechagua Coast. Tafadhali chagua kaunti:\n1. Mombasa\n2. Kilifi\n3. Kwale\n4. Lamu"
    elif text == "1*3":
        return "CON Umechagua Central. Tafadhali chagua kaunti:\n1. Nyeri\n2. Murang'a\n3. Kiambu\n4. Kirinyaga"
    elif text == "1*4":
        return "CON Umechagua Rift Valley. Tafadhali chagua kaunti:\n1. Nakuru\n2. Uasin Gishu\n3. Bomet"
    elif text == "1*5":
        return "CON Umechagua Western. Tafadhali chagua kaunti:\n1. Kakamega\n2. Bungoma\n3. Vihiga"
    elif text == "1*6":
        return "CON Umechagua Nyanza. Tafadhali chagua kaunti:\n1. Kisumu\n2. Homa Bay\n3. Migori"
    elif text == "1*7":
        return "CON Umechagua Eastern. Tafadhali chagua kaunti:\n1. Meru\n2. Embu\n3. Kitui"
    elif text == "1*8":
        return "CON Umechagua North Eastern. Tafadhali chagua kaunti:\n1. Garissa\n2. Wajir\n3. Mandera"

    # Handle county selection
    if text.startswith("1*"):
        selected_region = text.split('*')[1]
        region_name = list(regions_counties.keys())[int(selected_region) - 1]
        counties = regions_counties[region_name]
        return f"END Umechagua {region_name}. Kaunti zilizochaguliwa: {', '.join(counties)}."

    return "END Invalid choice. Please try again."

if __name__ == '__main__':  # Corrected to use __name__
    app.run(debug=True)


export GEMINI_API_KEY="AIzaSyD4X2KRt8r9TGD-8uUtAK_qWq58F_34big"

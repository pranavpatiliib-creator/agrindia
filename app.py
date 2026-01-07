
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from datetime import datetime
import json
import os
app = Flask(__name__)

# Session storage (in production, use Redis or database)
user_sessions = {}

# ==================== CROP DATABASE ====================
CROP_DATABASE = {
    "rice": {
        "name_marathi": "तांदूळ",
        "name_english": "Rice/Paddy",
        "scientific": "Oryza sativa",
        "season": "खरीप (Kharif)",
        "duration": "120-150 दिवस",
        "soil": "चिकणी माती / Clay loam",
        "ph": "5.5-7.0",
        "temp": "21-37°C",
        "seed_rate": "25-30 kg/हेक्टर",
        "spacing": "20 x 15 cm",
        "water": "उच्च - सतत पाणी 5-10 cm",
        "npk": "120:60:40",
        "msp": 2300,
        "yield": "50-60 क्विंटल/हेक्टर",
        "pests": ["तुडतुडे (Stem Borer)", "पाने गुंडाळणारा किडा", "गंधी बग"],
        "diseases": ["ब्लास्ट", "बॅक्टेरियल लीफ ब्लाइट", "शीथ ब्लाइट"]
    },
    "wheat": {
        "name_marathi": "गहू",
        "name_english": "Wheat",
        "scientific": "Triticum aestivum",
        "season": "रब्बी (Rabi)",
        "duration": "120-150 दिवस",
        "soil": "चिकणी दुमट माती / Clay loam",
        "ph": "6.0-7.5",
        "temp": "10-25°C",
        "seed_rate": "100-125 kg/हेक्टर",
        "spacing": "20-23 cm ओळींमध्ये",
        "water": "4-6 पाणी",
        "npk": "150:60:40",
        "msp": 2425,
        "yield": "40-50 क्विंटल/हेक्टर",
        "pests": ["तुडतुडे", "माहू (Aphids)", "टरमाइट"],
        "diseases": ["येलो रस्ट", "ब्राउन रस्ट", "Loose Smut"]
    },
    "jowar": {
        "name_marathi": "ज्वारी",
        "name_english": "Jowar/Sorghum",
        "scientific": "Sorghum bicolor",
        "season": "खरीफ व रब्बी (Kharif & Rabi)",
        "duration": "100-120 दिवस",
        "soil": "सर्व प्रकारची माती / All types",
        "ph": "6.0-8.5",
        "temp": "25-35°C",
        "seed_rate": "10-12 kg/हेक्टर",
        "spacing": "45 x 15 cm",
        "water": "मध्यम - 3-4 पाणी",
        "npk": "80:40:40",
        "msp": 3180,
        "yield": "25-30 क्विंटल/हेक्टर",
        "pests": ["तुडतुडे", "शूट फ्लाय", "पाने गुंडाळणारा"],
        "diseases": ["चार्कोल रॉट", "डाउनी मिल्ड्यू", "लीफ ब्लाइट"]
    },
    "bajra": {
        "name_marathi": "बाजरी",
        "name_english": "Bajra/Pearl Millet",
        "scientific": "Pennisetum glaucum",
        "season": "खरीफ (Kharif)",
        "duration": "70-90 दिवस",
        "soil": "वालुकामय दुमट / Sandy loam",
        "ph": "6.0-8.0",
        "temp": "25-35°C",
        "seed_rate": "4-5 kg/हेक्टर",
        "spacing": "45 x 15 cm",
        "water": "कमी - 2-3 पाणी",
        "npk": "80:40:20",
        "msp": 2500,
        "yield": "20-25 क्विंटल/हेक्टर",
        "pests": ["तुडतुडे", "शूट फ्लाय", "हेड माइट"],
        "diseases": ["डाउनी मिल्ड्यू", "अर्गॉट", "स्मट"]
    },
    "maize": {
        "name_marathi": "मका",
        "name_english": "Maize/Corn",
        "scientific": "Zea mays",
        "season": "खरीफ व रब्बी (Kharif & Rabi)",
        "duration": "90-110 दिवस",
        "soil": "चिकणी दुमट / Clay loam",
        "ph": "5.5-7.5",
        "temp": "21-27°C",
        "seed_rate": "20-25 kg/हेक्टर",
        "spacing": "60 x 20 cm",
        "water": "मध्यम - 4-6 पाणी",
        "npk": "120:60:40",
        "msp": 2090,
        "yield": "60-70 क्विंटल/हेक्टर",
        "pests": ["तुडतुडे", "फॉल आर्मीवर्म", "शूट फ्लाय"],
        "diseases": ["टर्सिकम लीफ ब्लाइट", "मेडिस लीफ ब्लाइट", "रस्ट"]
    },
    "cotton": {
        "name_marathi": "कापूस",
        "name_english": "Cotton",
        "scientific": "Gossypium spp.",
        "season": "खरीफ (Kharif)",
        "duration": "150-180 दिवस",
        "soil": "काळी माती / Black soil",
        "ph": "6.0-8.0",
        "temp": "21-30°C",
        "seed_rate": "15-20 kg/हेक्टर",
        "spacing": "90 x 60 cm",
        "water": "उच्च - 6-8 पाणी",
        "npk": "120:60:60",
        "msp": 7020,
        "yield": "20-25 क्विंटल/हेक्टर",
        "pests": ["बोंडवेविल", "अमेरिकन बोंडवेविल", "व्हाईट फ्लाय"],
        "diseases": ["विल्ट", "लीफ कर्ल", "रूट रॉट"]
    },
    "soybean": {
        "name_marathi": "सोयाबीन",
        "name_english": "Soybean",
        "scientific": "Glycine max",
        "season": "खरीफ (Kharif)",
        "duration": "90-110 दिवस",
        "soil": "चिकणी दुमट / Clay loam",
        "ph": "6.0-7.5",
        "temp": "20-30°C",
        "seed_rate": "70-80 kg/हेक्टर",
        "spacing": "45 x 5 cm",
        "water": "मध्यम - 3-5 पाणी",
        "npk": "30:60:40",
        "msp": 4892,
        "yield": "25-30 क्विंटल/हेक्टर",
        "pests": ["गर्डल बीटल", "लीफ माइनर", "स्टेम फ्लाय"],
        "diseases": ["येलो मोजेक", "बॅक्टेरियल पस्ट्यूल", "रूट रॉट"]
    },
    "groundnut": {
        "name_marathi": "शेंगदाणा",
        "name_english": "Groundnut/Peanut",
        "scientific": "Arachis hypogaea",
        "season": "खरीफ (Kharif)",
        "duration": "100-120 दिवस",
        "soil": "वालुकामय दुमट / Sandy loam",
        "ph": "6.0-7.0",
        "temp": "20-30°C",
        "seed_rate": "100-125 kg/हेक्टर",
        "spacing": "30 x 10 cm",
        "water": "मध्यम - 4-6 पाणी",
        "npk": "25:50:75",
        "msp": 6377,
        "yield": "20-25 क्विंटल/हेक्टर",
        "pests": ["थ्रिप्स", "जासीड", "हेलिकोव्हर्पा"],
        "diseases": ["टिक्का लीफ स्पॉट", "रस्ट", "बड नेक्रोसिस"]
    },
    "tur": {
        "name_marathi": "तूर",
        "name_english": "Tur/Arhar/Pigeon Pea",
        "scientific": "Cajanus cajan",
        "season": "खरीफ (Kharif)",
        "duration": "150-180 दिवस",
        "soil": "चिकणी दुमट / Clay loam",
        "ph": "6.5-7.5",
        "temp": "20-30°C",
        "seed_rate": "15-20 kg/हेक्टर",
        "spacing": "60 x 15 cm",
        "water": "कमी - 2-3 पाणी",
        "npk": "25:50:0",
        "msp": 7550,
        "yield": "15-20 क्विंटल/हेक्टर",
        "pests": ["पोड बोअरर", "पोड फ्लाय", "माईट"],
        "diseases": ["विल्ट", "स्टेरिलिटी मोजेक", "फायटोप्थोरा ब्लाइट"]
    },
    "gram": {
        "name_marathi": "हरभरा",
        "name_english": "Gram/Chana/Chickpea",
        "scientific": "Cicer arietinum",
        "season": "रब्बी (Rabi)",
        "duration": "100-120 दिवस",
        "soil": "चिकणी दुमट / Clay loam",
        "ph": "6.0-7.5",
        "temp": "20-25°C",
        "seed_rate": "75-80 kg/हेक्टर",
        "spacing": "30 x 10 cm",
        "water": "कमी - 2-3 पाणी",
        "npk": "20:40:20",
        "msp": 5440,
        "yield": "18-22 क्विंटल/हेक्टर",
        "pests": ["पोड बोअरर", "कट वर्म", "माहू"],
        "diseases": ["विल्ट", "ब्लाइट", "रूट रॉट"]
    },
    "onion": {
        "name_marathi": "कांदा",
        "name_english": "Onion",
        "scientific": "Allium cepa",
        "season": "रब्बी (Rabi)",
        "duration": "120-150 दिवस",
        "soil": "चिकणी दुमट / Clay loam",
        "ph": "6.0-7.0",
        "temp": "15-25°C",
        "seed_rate": "8-10 kg/हेक्टर",
        "spacing": "15 x 10 cm",
        "water": "उच्च - 10-15 पाणी",
        "npk": "100:50:50",
        "msp": "बाजार आधारित",
        "yield": "250-300 क्विंटल/हेक्टर",
        "pests": ["थ्रिप्स", "कट वर्म", "माईट"],
        "diseases": ["पर्पल ब्लॉच", "स्टेमफिलियम ब्लाइट", "बेसल रॉट"]
    }
}

# ==================== MENU FUNCTIONS ====================
def get_main_menu():
    return """🌾 *AgriIndia*

नमस्कार! तुम्हाला कशात मदत करू?

1️⃣ पीक माहिती (Crop Information)
2️⃣ MSP दर (MSP Rates)
3️⃣ हवामान (Weather)
4️⃣ सरकारी योजना (Govt Schemes)
5️⃣ किड व रोग व्यवस्थापन (Pest Management)
6️⃣ तज्ञ मदत (Expert Help)

📝 कृपया क्रमांक पाठवा (1-6)"""

def get_crop_categories():
    return """🌾 *पीक प्रकार निवडा*

1️⃣ खरीप पिके (Kharif - पावसाळी)
2️⃣ रब्बी पिके (Rabi - हिवाळी)
3️⃣ नगदी पिके (Cash Crops)
4️⃣ कडधान्य (Pulses)
5️⃣ भाजीपाला (Vegetables)

📝 क्रमांक पाठवा (1-5)
🔙 मुख्य मेनू: 0"""

def get_kharif_crops():
    return """🌾 *खरीप पिके (Kharif Crops)*

1️⃣ तांदूळ (Rice)
2️⃣ ज्वारी (Jowar)
3️⃣ बाजरी (Bajra)
4️⃣ मका (Maize)
5️⃣ तूर (Tur Dal)
6️⃣ सोयाबीन (Soybean)
7️⃣ कापूस (Cotton)
8️⃣ शेंगदाणा (Groundnut)

📝 पीक क्रमांक पाठवा (1-8)
🔙 मागे: 0"""

def get_rabi_crops():
    return """❄️ *रब्बी पिके (Rabi Crops)*

1️⃣ गहू (Wheat)
2️⃣ हरभरा (Gram/Chana)
3️⃣ कांदा (Onion)
4️⃣ लसूण (Garlic)
5️⃣ सरसो (Mustard)

📝 पीक क्रमांक पाठवा (1-5)
🔙 मागे: 0"""

def get_crop_details(crop_key):
    """Get detailed information about a specific crop"""
    crop = CROP_DATABASE.get(crop_key)
    if not crop:
        return "माहिती उपलब्ध नाही / Information not available"
    
    return f"""🌾 *{crop['name_marathi']} / {crop['name_english']}*

━━━━━━━━━━━━━━━━━━━━━
📋 *मूलभूत माहिती*
• वैज्ञानिक नाव: {crop['scientific']}
• पीक हंगाम: {crop['season']}
• पीक कालावधी: {crop['duration']}

━━━━━━━━━━━━━━━━━━━━━
🏞️ *माती व हवामान*
• माती: {crop['soil']}
• pH मूल्य: {crop['ph']}
• तापमान: {crop['temp']}

━━━━━━━━━━━━━━━━━━━━━
🌱 *पेरणी तपशील*
• बियाणे प्रमाण: {crop['seed_rate']}
• अंतर: {crop['spacing']}

━━━━━━━━━━━━━━━━━━━━━
💧 *पाणी व खत*
• पाणी गरज: {crop['water']}
• NPK शिफारस: {crop['npk']}

━━━━━━━━━━━━━━━━━━━━━
💰 *MSP आणि उत्पन्न*
• MSP 2024-25: ₹{crop['msp']}/क्विंटल
• अपेक्षित उत्पन्न: {crop['yield']}

━━━━━━━━━━━━━━━━━━━━━
🐛 *मुख्य किडे:*
{chr(10).join(f"• {pest}" for pest in crop['pests'])}

🦠 *मुख्य रोग:*
{chr(10).join(f"• {disease}" for disease in crop['diseases'])}

━━━━━━━━━━━━━━━━━━━━━
अधिक तपशीलासाठी:
1️⃣ पूर्ण पेरणी माहिती
2️⃣ खत व्यवस्थापन
3️⃣ किड नियंत्रण
4️⃣ बाजारभाव
0️⃣ मागे जा"""

def get_msp_rates():
    """Get MSP rates for major crops"""
    return """💰 *MSP दर 2024-25 (रुपये/क्विंटल)*

*खरीप पिके:*
• धान (Paddy): ₹2,300
• ज्वारी (Jowar): ₹3,180
• बाजरी (Bajra): ₹2,500
• मका (Maize): ₹2,090
• तूर (Tur): ₹7,550
• उडीद (Urad): ₹6,950
• मूग (Moong): ₹8,558
• सोयाबीन (Soybean): ₹4,892
• शेंगदाणा (Groundnut): ₹6,377
• कापूस (Cotton): ₹7,020

*रब्बी पिके:*
• गहू (Wheat): ₹2,425
• हरभरा (Gram): ₹5,440
• मसूर (Masoor): ₹6,425
• सरसो (Mustard): ₹5,650

📝 कृपया नोंद घ्या: हे केंद्र सरकारचे किमान आधार भाव आहेत.

🔙 मुख्य मेनू: 0"""

def get_pest_management():
    return """🐛 *किड व रोग व्यवस्थापन*

कोणत्या पिकाविषयी माहिती हवी आहे?

1️⃣ तांदूळ (Rice)
2️⃣ कापूस (Cotton)
3️⃣ भाजीपाला (Vegetables)
4️⃣ तूर (Tur)
5️⃣ सोयाबीन (Soybean)

📝 क्रमांक पाठवा (1-5)
🔙 मागे: 0"""

def get_govt_schemes():
    return """🏛️ *प्रमुख शेती योजना*

1️⃣ PM-KISAN (₹6000/वर्ष)
2️⃣ पीक विमा योजना (Crop Insurance)
3️⃣ मृदा स्वास्थ्य कार्ड
4️⃣ कृषी कर्ज (KCC)
5️⃣ सौर पंप योजना

📝 तपशीलासाठी क्रमांक पाठवा (1-5)
🔙 मागे: 0"""

def get_weather_info():
    return """🌤️ *हवामान माहिती*

कृपया तुमचा जिल्हा नाव पाठवा.

उदाहरण: अहमदनगर, पुणे, नाशिक

किंवा:
0️⃣ मुख्य मेनू"""

def get_expert_help():
    return """📞 *तज्ञ मदत*

*कृषी सल्लागार हेल्पलाइन:*
📱 किसान कॉल सेंटर: 1800-180-1551

*महाराष्ट्र कृषी विभाग:*
📱 020-26123232

*आणीबाणी मदत:*
📱 कृषी अधिकारी: 1800-233-1715

*WhatsApp सल्ला:*
📱 +91-XXXXXXXXXX (AgriIndia)

कृपया कार्यालयीन वेळेत (10 AM - 5 PM) संपर्क साधा.

🔙 मुख्य मेनू: 0"""

# ==================== SESSION MANAGEMENT ====================
def get_user_state(phone_number):
    """Get user's current state in menu navigation"""
    if phone_number not in user_sessions:
        user_sessions[phone_number] = {
            'state': 'main_menu',
            'previous_state': None,
            'data': {}
        }
    return user_sessions[phone_number]

def set_user_state(phone_number, state, data=None):
    """Set user's state and store any additional data"""
    session = get_user_state(phone_number)
    session['previous_state'] = session['state']
    session['state'] = state
    if data:
        session['data'].update(data)

# ==================== MESSAGE HANDLER ====================
def handle_message(message, phone_number):
    """Main message handling logic with state management"""
    message = message.strip().lower()
    session = get_user_state(phone_number)
    current_state = session['state']
    
    # Handle going back
    if message == '0':
        if current_state == 'main_menu':
            return get_main_menu()
        elif current_state in ['crop_categories', 'msp_rates', 'weather', 'schemes', 'pest', 'expert']:
            set_user_state(phone_number, 'main_menu')
            return get_main_menu()
        elif current_state in ['kharif_crops', 'rabi_crops']:
            set_user_state(phone_number, 'crop_categories')
            return get_crop_categories()
        elif current_state.startswith('crop_detail_'):
            # Go back to crop list
            prev_category = session['data'].get('crop_category', 'kharif')
            set_user_state(phone_number, f'{prev_category}_crops')
            return get_kharif_crops() if prev_category == 'kharif' else get_rabi_crops()
    
    # Handle different states
    if current_state == 'main_menu':
        if message == '1':
            set_user_state(phone_number, 'crop_categories')
            return get_crop_categories()
        elif message == '2':
            set_user_state(phone_number, 'msp_rates')
            return get_msp_rates()
        elif message == '3':
            set_user_state(phone_number, 'weather')
            return get_weather_info()
        elif message == '4':
            set_user_state(phone_number, 'schemes')
            return get_govt_schemes()
        elif message == '5':
            set_user_state(phone_number, 'pest')
            return get_pest_management()
        elif message == '6':
            set_user_state(phone_number, 'expert')
            return get_expert_help()
        else:
            return get_main_menu()
    
    elif current_state == 'crop_categories':
        if message == '1':
            set_user_state(phone_number, 'kharif_crops', {'crop_category': 'kharif'})
            return get_kharif_crops()
        elif message == '2':
            set_user_state(phone_number, 'rabi_crops', {'crop_category': 'rabi'})
            return get_rabi_crops()
        elif message == '3' or message == '4' or message == '5':
            return "ही माहिती लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        else:
            return get_crop_categories()
    
    elif current_state == 'kharif_crops':
        crop_map = {
            '1': 'rice', '2': 'jowar', '3': 'bajra', '4': 'maize',
            '5': 'tur', '6': 'soybean', '7': 'cotton', '8': 'groundnut'
        }
        if message in crop_map:
            crop_key = crop_map[message]
            set_user_state(phone_number, f'crop_detail_{crop_key}', {'current_crop': crop_key})
            return get_crop_details(crop_key)
        else:
            return get_kharif_crops()
    
    elif current_state == 'rabi_crops':
        crop_map = {
            '1': 'wheat', '2': 'gram', '3': 'onion'
        }
        if message in crop_map:
            crop_key = crop_map[message]
            set_user_state(phone_number, f'crop_detail_{crop_key}', {'current_crop': crop_key})
            return get_crop_details(crop_key)
        elif message == '4' or message == '5':
            return "ही माहिती लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        else:
            return get_rabi_crops()
    
    elif current_state.startswith('crop_detail_'):
        # Handle sub-options for crop details
        if message == '1':
            return "पूर्ण पेरणी माहिती लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        elif message == '2':
            return "खत व्यवस्थापन तपशील लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        elif message == '3':
            return "किड नियंत्रण माहिती लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        elif message == '4':
            return "बाजारभाव माहिती लवकरच उपलब्ध होईल.\n\n🔙 मागे: 0"
        else:
            current_crop = session['data'].get('current_crop')
            return get_crop_details(current_crop) if current_crop else get_main_menu()
    
    # Default: return to main menu
    set_user_state(phone_number, 'main_menu')
    return get_main_menu()

# ==================== FLASK ROUTES ====================

@app.route("/bot", methods=["POST"])
@app.route("/whatsapp", methods=["POST"])   # both supported
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    phone_number = request.values.get("From", "")

    print(f"📩 WhatsApp | From: {phone_number} | Msg: {incoming_msg}")

    try:
        response_text = handle_message(incoming_msg, phone_number)
    except Exception as e:
        print("❌ Bot Error:", e)
        response_text = "⚠️ काहीतरी चूक झाली आहे. कृपया पुन्हा प्रयत्न करा."

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)


@app.route('/')
def index():
    """Home page"""
    return """
    <h1>🌾 AgriIndia WhatsApp Bot</h1>
    <p>Status: ✅ Active</p>
    <p>Version: Stable Production</p>
    """


@app.route('/health')
def health():
    """Health check"""
    return {
        "status": "healthy",
        "time": datetime.now().isoformat()
    }


# ==================== START SERVER ====================
if __name__ == '__main__':
    print("🌾 AgriIndia WhatsApp Bot Starting...")
    print("📱 Twilio Webhook: /bot")
    print("✅ Health Check: /health")
    print("🚀 Server running on port 5000")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
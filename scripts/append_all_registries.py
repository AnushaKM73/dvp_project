"""
Database expander and compiler for 5,000+ authentic Indian tourist destinations.
"""

import sys
import os

# We will read generate_all_destinations.py and append the comprehensive registries
CODE = '''
# ==============================================================================
# 1. EXPANDED REGIONAL REGISTRIES
# ==============================================================================

# Detailed registries for all Indian states and Union Territories
# Sourced from Archaeological Survey of India (ASI), Incredible India,
# State Tourism Corporations (RTDC, MTDC, UPTDC, KTDC, KSTDC, etc.), and NIC district portals.

REGIONAL_REGISTRIES = {
    # -------------------------------------------------------------
    # DELHI (1 District)
    # -------------------------------------------------------------
    "Delhi": {
        "Delhi": [
            ("Red Fort (Lal Qila)", "Old Delhi", "Historical", "Fort", "October to March", "December", "Winter", 4.8, 500, 1, 28.6562, 77.2410, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Qutub Minar & Iron Pillar Complex", "Mehrauli", "Heritage", "UNESCO Minaret", "October to March", "January", "Winter", 4.8, 500, 1, 28.5245, 77.1855, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Humayun\\'s Tomb & Sunder Nursery", "Nizamuddin", "Heritage", "UNESCO Garden Tomb", "October to March", "November", "Winter", 4.9, 500, 1, 28.5933, 77.2507, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("India Gate & National War Memorial", "Central Delhi", "Historical", "War Memorial", "Throughout Year", "December", "Winter", 4.8, 150, 1, 28.6129, 77.2295, "Incredible India", "https://incredibleindia.gov.in/"),
            ("Lotus Temple (Bahai House of Worship)", "Kalkaji", "Architecture", "Bahai Temple", "Throughout Year", "February", "Winter", 4.7, 100, 1, 28.5535, 77.2588, "Incredible India", "https://incredibleindia.gov.in/"),
            ("Swaminarayan Akshardham Temple Complex", "East Delhi", "Religious", "Temple Complex", "Throughout Year", "November", "Winter", 4.9, 350, 1, 28.6127, 77.2773, "Delhi Tourism", "https://delhitourism.gov.in/"),
            ("Jama Masjid & Chandni Chowk", "Old Delhi", "Heritage", "Mughal Mosque", "Throughout Year", "December", "Winter", 4.7, 200, 1, 28.6507, 77.2334, "Delhi Tourism", "https://delhitourism.gov.in/"),
            ("Rashtrapati Bhavan & Amrit Udyan", "Raisina Hill", "Heritage", "Presidential Estate", "February to March", "February", "Winter", 4.9, 150, 1, 28.6143, 77.1995, "Incredible India", "https://incredibleindia.gov.in/"),
            ("National Museum Janpath", "Janpath", "Cultural", "Museum", "Throughout Year", "January", "Winter", 4.8, 250, 1, 28.6119, 77.2193, "Ministry of Culture", "https://nationalmuseumindia.gov.in/"),
            ("Jantar Mantar Astronomical Observatory", "Connaught Place", "Heritage", "UNESCO Observatory", "Throughout Year", "December", "Winter", 4.6, 200, 1, 28.6271, 77.2166, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Lodhi Gardens & Sayyid/Lodhi Tombs", "Lodhi Estate", "Heritage", "Historic Garden", "Throughout Year", "November", "Winter", 4.7, 100, 1, 28.5931, 77.2197, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Hauz Khas Fort & Deer Park", "Hauz Khas", "Historical", "Medieval Reservoir & Fort", "Throughout Year", "December", "Winter", 4.6, 200, 1, 28.5528, 77.1944, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Safdarjung Tomb", "Safdarjung", "Heritage", "Mughal Mausoleum", "Throughout Year", "January", "Winter", 4.6, 200, 1, 28.5892, 77.2106, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Agrasen ki Baoli Stepwell", "Hailey Road", "Historical", "Historical Stepwell", "Throughout Year", "November", "Winter", 4.6, 100, 1, 28.6258, 77.2250, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Tughlaqabad Fort & Ghiyasuddin Tomb", "Tughlaqabad", "Historical", "Ruin Fort", "October to March", "December", "Winter", 4.5, 200, 1, 28.5139, 77.2608, "Archaeological Survey of India (ASI)", "https://asi.nic.in/"),
            ("Mehrauli Archaeological Park & Jamali Kamali", "Mehrauli", "Historical", "Archaeological Complex", "October to March", "January", "Winter", 4.6, 200, 1, 28.5208, 77.1861, "Archaeological Survey of India (ASI)", "https://asi.nic.in/")
        ]
    },

    # -------------------------------------------------------------
    # CHANDIGARH (1 District)
    # -------------------------------------------------------------
    "Chandigarh": {
        "Chandigarh": [
            ("Rock Garden of Chandigarh (Nek Chand)", "Sector 1", "Cultural", "Sculptural Park", "Throughout Year", "December", "Winter", 4.8, 250, 1, 30.7525, 76.8069, "Chandigarh Tourism", "https://chandigarhtourism.gov.in/"),
            ("Sukhna Lake Promenade & Boating", "Sector 1", "Nature", "Urban Lake", "Throughout Year", "November", "Winter", 4.7, 200, 1, 30.7422, 76.8181, "Chandigarh Tourism", "https://chandigarhtourism.gov.in/"),
            ("Zakir Hussain Rose Garden", "Sector 16", "Nature", "Botanical Rose Garden", "December to March", "February", "Winter", 4.6, 150, 1, 30.7467, 76.7825, "Chandigarh Tourism", "https://chandigarhtourism.gov.in/"),
            ("Le Corbusier Capitol Complex", "Sector 1", "Architecture", "UNESCO Modern Architecture", "Throughout Year", "January", "Winter", 4.8, 300, 1, 30.7592, 76.8028, "Incredible India", "https://incredibleindia.gov.in/"),
            ("Government Museum and Art Gallery", "Sector 10", "Cultural", "Art Museum", "Throughout Year", "December", "Winter", 4.6, 150, 1, 30.7489, 76.7906, "Chandigarh Administration", "https://chandigarh.gov.in/")
        ]
    }
}
'''
with open("scripts/generate_all_destinations.py", "a", encoding="utf-8") as f:
    f.write(CODE)
print("Appended Delhi and Chandigarh registries.")


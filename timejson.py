import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import json
import time

# Load country data
df = pd.read_csv("country_code.csv")
country_names = df['name'].dropna().unique().tolist()

# Set up geolocator and timezone finder
geolocator = Nominatim(user_agent="timezone_mapper")
tf = TimezoneFinder()

# Dictionary to hold mapping
country_timezone_map = {}

for country in country_names:
    try:
        location = geolocator.geocode(country, timeout=10)
        if location:
            tz = tf.timezone_at(lat=location.latitude, lng=location.longitude)
            if tz:
                country_timezone_map[country] = tz
                print(f"{country} → {tz}")
            else:
                print(f"⚠️ Timezone not found for {country}")
        else:
            print(f"⚠️ Could not geocode {country}")
    except Exception as e:
        print(f"❌ Error processing {country}: {e}")
    time.sleep(1)  # Delay to prevent hitting API rate limits

# Save to JSON
with open("country_timezones.json", "w") as f:
    json.dump(country_timezone_map, f, indent=2)

print("\n✅ country_timezones.json created!")

#gui
import tkinter as tk 
from tkinter import ttk
from tkinter import *

#time
from datetime import datetime
import pytz
import calendar

#data
from collections import OrderedDict
import pandas as pd
import json
import mysql.connector
import requests

#plots
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#imp keys
from dotenv import load_dotenv
import os

load_dotenv()

#------------------------------------------------------------------------------------------------------------------------------------------------------------

# API key
api_key=os.getenv("api_key")

# load CSVs
countries_df = pd.read_csv("country_code.csv")
states_df = pd.read_csv("states.csv")           

country_name_list = countries_df['name'].dropna().tolist()

with open("country_timezones.json") as f:
    country_timezone_map = json.load(f)

# to hold selected location
_country = None
_state = None
_city = None

#------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_dashboard():

    def update_time():
        selected_country = country_combobox.get()
        tz_name = country_timezone_map.get(selected_country)

        if tz_name:
            try:
                tz = pytz.timezone(tz_name)
                now = datetime.now(tz)
            except:
                now = datetime.now()
        else:
            now = datetime.now()

        time_str = now.strftime("%A, %d %B %Y\n%I:%M:%S %p")
        datetime_label.config(text=time_str)
        root.after(1000, update_time)

#------------------------------------------------------------------------------------------------------------------------------------------------------------

    def update_states(event=None):
        selected_country_name = country_combobox.get()
        country_row = countries_df[countries_df['name'] == selected_country_name]
        if not country_row.empty:
            country_code = country_row.iloc[0]['code']
            filtered_states = states_df[states_df['country_code'] == country_code]['state'].dropna().tolist()
            state_combobox['values'] = filtered_states
            state_combobox.set("Choose State")
        else:
            state_combobox['values'] = []
            state_combobox.set("")

#Weather Data
#------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_weather():
        
        global _country, _state, _city, api_key
        _country = country_combobox.get()
        _state = state_combobox.get()
        _city = city_entry.get()

        if _country and _country != "Choose Country" and _state and _state != "Choose State" and _city and _city.strip() != "":

            weather_info.config( text=f"🌐 Getting weather for: {_city}, {_state}, {_country}")

            api_url=f"http://api.openweathermap.org/geo/1.0/direct?q={_city},{_state},{_country}&limit=1&appid={api_key}"
            r=requests.get(api_url)
            data1=r.json()
            
            if data1:
                lat = data1[0].get('lat')
                lon = data1[0].get('lon')
                weather_info.config( text=f"📍 Latitude: {lat}, Longitude: {lon}")
                
            #CURRENT weather
            #-----------------------------------------------------------------------------------------------------------------------------------------------

                api_url2=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
                r2=requests.get(api_url2)
                data=r2.json()
                
                if not data:
                    weather_info.config( text="❌ No weather data available.")
                else:
                    weather_main = data.get('weather', [{}])[0].get('main', '')
                    weather_desc = data.get('weather', [{}])[0].get('description', '')

                    #converting to celsius 
                    temp = data.get('main', {}).get('temp', 0) - 273.15
                    feels_like = data.get('main', {}).get('feels_like', 0) - 273.15 
                    humidity = data.get('main', {}).get('humidity', 0)
                    pressure = data.get('main', {}).get('pressure', 0)
                    wind_speed = data.get('wind', {}).get('speed', 0)
                    cloudiness = data.get('clouds', {}).get('all', 0)

                    msg = (
                        f"📍 Weather Info for {_city}, {_country}\n"
                        f"──────────────────────────────\n"
                        f"🌤 Condition   : {weather_main} ({weather_desc.title()})\n"
                        f"🌡 Temperature : {temp:.1f}°C (Feels like {feels_like:.1f}°C)\n"
                        f"💧 Humidity    : {humidity}%\n"
                        f"📈 Pressure    : {pressure} hPa\n"
                        f"💨 Wind Speed  : {wind_speed} m/s\n"
                        f"☁️ Cloud Cover : {cloudiness}%\n"
                        f"──────────────────────────────")

                    weather_info.config(text=msg)

            # 5-DAY weather
            #------------------------------------------------------------------------------------------------------------------------------------------

                api_url3 = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
                r3 = requests.get(api_url3)
                data3 = r3.json()

                # daily temp by date
                daily_forecasts = OrderedDict()
                for entry in data3.get("list", []):
                    dt_txt = entry["dt_txt"]
                    if "12:00:00" in dt_txt:
                        date = dt_txt.split(" ")[0]
                        temp_min = entry["main"]["temp_min"] - 273.15
                        temp_max = entry["main"]["temp_max"] - 273.15

                        # date to weekday
                        day = datetime.strptime(date, "%Y-%m-%d").strftime("%a")

                        # emoji
                        max_temp = entry["main"]["temp_max"] - 273.15
                        if max_temp >= 32:
                            emoji = "🥵"
                        elif max_temp >= 28:
                            emoji = "🌞"
                        elif max_temp >= 24:
                            emoji = "🌤"
                        elif max_temp >= 20:
                            emoji = "⛅"
                        else:
                            emoji = "🌧"

                        daily_forecasts[day] = f"{emoji} {day}: 🔼{temp_max:.1f}°C 🔽{temp_min:.1f}°C"

                forecast = "📅 5-Day Forecast:\n\n" + "   |   ".join(daily_forecasts.values())
                forecast_label.config(text=forecast)

            #------------------------------------------------------------------------------------------------------------------------------------------------------------                

            else:
               weather_info.config( text="❌ Invalid Location!")
        else:
            weather_info.config( text="⚠️ Please select a valid country, state, and city.")

#Weather Analysis
#------------------------------------------------------------------------------------------------------------------------------------------------------------

    def open_analyze_window():
        analyze_win = Toplevel(root)
        analyze_win.title("📊 Weather Data Analysis")
        analyze_win.configure(bg="#f5f3ff")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#f5f3ff", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="white", background="#6C63FF")
        style.configure("TCombobox", padding=5, font=("Segoe UI", 10))

        # Labels
        ttk.Label(analyze_win, text="Select City").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        ttk.Label(analyze_win, text="Select Metric").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        ttk.Label(analyze_win, text="Select Year").grid(row=2, column=0, padx=10, pady=5, sticky=W)

        cities = ["Coimbatore", "Vellore", "Chennai"]
        metrics = {
            "Average Temperature": "avg_temp",
            "Highest Temperature": "highest_temp",
            "Lowest Temperature": "lowest_temp",
            "Average Wind Speed": "avg_wind_speed",
            "Average Humidity": "avg_humidity",
            "Average Rain Level": "avg_rain_level",
            "Average UV Index": "avg_uv_index"
        }
        years = ["2022", "2023", "2024"]

        city_var = StringVar(analyze_win)
        metric_var = StringVar(analyze_win)
        year_var = StringVar(analyze_win)

        city_menu = ttk.Combobox(analyze_win, textvariable=city_var, values=cities, state="readonly")
        metric_menu = ttk.Combobox(analyze_win, textvariable=metric_var, values=list(metrics.keys()), state="readonly")
        year_menu = ttk.Combobox(analyze_win, textvariable=year_var, values=years, state="readonly")

        city_menu.grid(row=0, column=1, padx=10, pady=5)
        metric_menu.grid(row=1, column=1, padx=10, pady=5)
        year_menu.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(analyze_win, text="Plot", command=lambda: plot_analysis(analyze_win, city_var.get(), metric_var.get(), year_var.get(), metrics)).grid(row=3, column=0, columnspan=2, pady=15)

#Plots
#------------------------------------------------------------------------------------------------------------------------------------------------------------

    def plot_analysis(window, city, metric_label, year, metrics):
        metric_col = metrics[metric_label]

        mycon = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = mycon.cursor()

        query = f"""
            SELECT month, AVG({metric_col})
            FROM weather_data
            WHERE city_name = %s AND year = %s
            GROUP BY month
            ORDER BY FIELD(month,
                'January','February','March','April','May','June',
                'July','August','September','October','November','December'
            )
        """
        cursor.execute(query, (city, year))
        results = cursor.fetchall()
        cursor.close()
        mycon.close()

        if not results:
            return

        months = [row[0] for row in results]
        values = [row[1] for row in results]

        color1 = "#6C63FF"  # main purple
        color2 = "#FF6584"  # accent pink

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.plot(months, values, marker='o', linestyle='-', linewidth=2, color=color1, markerfacecolor=color2)
        ax.set_title(f"{metric_label} in {city} - {year}", fontsize=12, fontweight='bold', color="#4b3832", fontname="Segoe UI")
        ax.set_xlabel("Month", fontsize=10, fontname="Segoe UI")
        ax.set_ylabel(metric_label, fontsize=10, fontname="Segoe UI")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_facecolor("#fdf6ff")

        # Rotate months for clarity
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=30, ha="right", fontsize=9)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=4, column=0, columnspan=2, pady=10)
        
#USER interface
#------------------------------------------------------------------------------------------------------------------------------------------------------------            

    # main window
    root = tk.Tk()
    root.title("Weather Dashboard")
    root.geometry("850x650")
    root.minsize(600, 400)
    root.configure(bg="#f5f3ff")

    # title
    title_label = tk.Label(root,
                           text="⭐ Lyra Forecast ⭐",
                           font=("Segoe UI", 26, "bold"),
                           fg="#6C63FF",
                           bg="#f5f3ff")
    title_label.pack(pady=10)

    # date/time
    datetime_label = tk.Label(root,
                              font=("Segoe UI", 12),
                              fg="#333333",
                              bg="#f5f3ff")
    datetime_label.pack()

    # select location
    location_title = tk.Label(root,
                              text="📍 Select Location",
                              font=("Segoe UI", 13, "bold"),
                              fg="#FF6584",
                              bg="#f5f3ff")
    location_title.pack(pady=15)

    # location inputs
    input_frame = tk.Frame(root, bg="#f5f3ff")
    input_frame.pack(pady=10, padx=40)

    # Country
    tk.Label(input_frame, text="Country:", bg="#f5f3ff", font=("Segoe UI", 12)).grid(row=0, column=0, padx=5, pady=5)
    country_combobox = ttk.Combobox(input_frame, values=country_name_list, state="readonly", font=("Segoe UI", 10))
    country_combobox.grid(row=0, column=1, padx=10, pady=5)
    country_combobox.set("Choose Country")
    country_combobox.bind("<<ComboboxSelected>>", update_states)

    # State
    tk.Label(input_frame, text="State:", bg="#f5f3ff", font=("Segoe UI", 12)).grid(row=0, column=2, padx=5)
    state_combobox = ttk.Combobox(input_frame, state="readonly", font=("Segoe UI", 10))
    state_combobox.grid(row=0, column=3, padx=10)
    state_combobox.set("Choose State")

    # City
    tk.Label(input_frame, text="City:", bg="#f5f3ff", font=("Segoe UI", 12)).grid(row=0, column=4, padx=5)
    city_entry = tk.Entry(input_frame, font=("Segoe UI", 10))
    city_entry.grid(row=0, column=5, padx=10)

    # get weather button
    get_weather_button = tk.Button(root,
                                   text="Get Weather",
                                   font=("Segoe UI", 11, "bold"),
                                   bg="#6C63FF",  
                                   fg="white",  
                                   command=get_weather)
    get_weather_button.pack(pady=10)

    # analyze weather
    analyze_button = tk.Button(root,
                           text="Analyze Weather",
                           font=("Segoe UI", 11, "bold"),
                           bg="#FF6584",
                           fg="white",
                           command=open_analyze_window)
    analyze_button.pack(pady=5)

    # weather info box
    weather_frame = tk.LabelFrame(root,
                                  text="🌦 Weather Info",
                                  font=("Segoe UI", 13, "bold"),
                                  fg="#6C63FF",
                                  bg="white",
                                  width=700,
                                  height=300,
                                  padx=15,
                                  pady=15,
                                  labelanchor="n")
    weather_frame.pack(padx=30, pady=25, fill="both", expand=True)

    weather_info = tk.Label(weather_frame,
                            text="⏳ Please select location and click 'Get Weather'...",
                            font=("Segoe UI", 12),
                            justify="left",
                            anchor="nw",
                            bg="white",
                            fg="#333333")
    weather_info.pack(fill="both", expand=True, anchor="nw")

    forecast_label = tk.Label(weather_frame,
                          text="",
                          font=("Segoe UI", 11),
                          justify="left",
                          anchor="nw",
                          bg="white",
                          fg="#6C63FF")
    forecast_label.pack(fill="x", anchor="nw", pady=(10, 0))

#------------------------------------------------------------------------------------------------------------------------------------------------------------
   
    update_time();
    root.mainloop()

#------------------------------------------------------------------------------------------------------------------------------------------------------------

create_dashboard()

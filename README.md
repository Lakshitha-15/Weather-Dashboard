# Weather-Dashboard

Lyra Forecast — The Weather Dashboard is a Python-based application that displays real-time weather information using an external API (OpenWeather) and visualizes historical weather trends using existing data stored in a MySQL database. The project focuses on API integration, database connectivity, data analysis, and graphical visualization through a user-friendly GUI.

Features:
- Fetches real-time weather data using OpenWeather API
- Visualizes historical weather trends using pre-existing MySQL data
- Connects to a MySQL database for reading and analysis
- Interactive GUI built using Tkinter

Technologies Used:
- Programming Language: Python
- GUI: Tkinter
- API: OpenWeather API
- Database: MySQL
- Data Visualization: Matplotlib
- Libraries: requests, mysql-connector-python, matplotlib

Database Setup
This project uses an existing MySQL database provided as a `.sql` file.

- Import `weather_data.sql` into MySQL before running the application  
- The application performs **read-only operations** on the database  
- The data is used for historical weather analysis and visualization  


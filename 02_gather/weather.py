import requests

api_key = "1faaf406ffd3a1d04bcc69879f233cd7"
city= "portland"
state= "Oregon"

geo_url= f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state}&limit=2&appid={api_key}"

response = requests.get(geo_url)

if response.status_code == 200:
    data = response.json()
    if data:
        location = data[0]  
        latitude = location["lat"]
        longitude = location["lon"]
    else:
        print("No data found for the location.")
else:
    print("Failed to retrieve data from the API.")


weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

response = requests.get(weather_url)

x = response.json()

if x["cod"] != "404":

	y = x["main"]
	z = x["weather"]

	weather_description = z[0]["description"]
	if(weather_description.lower() == 'rain'):
		print("Right now, it is raining in Portland, OR.")
	else:
		print("Right now, it is not raining in Portland, OR.")

else:
	print(" City Not Found ")

date_to_check = "2024-04-15 15:00:00"
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}"
response = requests.get(forecast_url)



if response.status_code == 200:
    forecast_data = response.json()
    if forecast_data["cod"] == "200":
        for forecast in forecast_data["list"]:
            if forecast["dt_txt"] == date_to_check:
                weather_des= forecast["weather"][0]["description"]
                if  weather_des.lower() == 'rain':
                    print("It will be raining for our next class.")
                else:
                    print("It won't be raining for our next class. weather for our next class is :", weather_des)
                     
                break
    else:
        print("unable retrieve forecast data.")
else:
    print("unable to retrieve forecast data.")


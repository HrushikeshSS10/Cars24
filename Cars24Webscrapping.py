# IMPORT LIBRARIES
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# SETUP CHROME DRIVER
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# OPEN WEBSITE
url = "https://www.cars24.com/buy-used-renault-cars-mumbai/"
driver.get(url)
time.sleep(6)  # wait for page to load

# AUTO-SCROLL TO LOAD ALL CARS
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(6)  # wait for new cars to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# FIND ALL CAR CARDS
cars = driver.find_elements(By.CLASS_NAME, "styles_normalCardWrapper__qDZjq")
if not cars:
    cars = driver.find_elements(By.XPATH, "//div[contains(@class,'normalCardWrapper')]")
print("Total cars found:", len(cars))

# LISTS TO STORE DATA
car_names = []
car_prices = []
car_type = []
car_yom = []
car_km = []
car_location = []
car_trans = []
car_owner = []   # new owner list

for car in cars:
    # NAME + YEAR
    try:
        name_raw = car.find_element(By.CSS_SELECTOR, "span.sc-braxZu.kjFjan").text.strip()
        parts = name_raw.split(" ", 1)
        year = parts[0] if parts[0].isdigit() else None
        name = parts[1] if year and len(parts) > 1 else name_raw
    except:
        name, year = (None, None)

    # PRICE
    try:
        price = car.find_element(By.CSS_SELECTOR, "p.sc-braxZu.cyPhJl").text.strip()
    except:
        price = None

    # DETAILS: km, fuel, transmission, owner
    km = fuel_type = transmission = owner = None
    try:
        details = car.find_elements(By.CSS_SELECTOR, "p.sc-braxZu.kvfdZL")
        for d in details:
            txt = d.text.strip()
            low = txt.lower()
            if "km" in low and km is None:
                km = txt
            elif any(f in low for f in ["petrol", "diesel", "cng", "lpg", "electric", "hybrid"]) and fuel_type is None:
                fuel_type = txt
            elif any(t in low for t in ["manual", "automatic", "cvt", "am/s", "mt", "at"]) and transmission is None:
                transmission = txt
            elif "owner" in low and owner is None:
                owner = txt
    except:
        pass

    # LOCATION
    try:
        location = car.find_element(By.CSS_SELECTOR, "p.sc-braxZu.lmmumg").text.strip()
    except:
        location = None

    # APPEND VALUES
    car_names.append(name)
    car_prices.append(price)
    car_yom.append(year)
    car_km.append(km)
    car_type.append(fuel_type)
    car_trans.append(transmission)
    car_owner.append(owner)
    car_location.append(location)

# CREATE DATAFRAME
df = pd.DataFrame({
    "Car Name": car_names,
    "Price": car_prices,
    "Year": car_yom,
    "KM Driven": car_km,
    "Fuel Type": car_type,
    "Transmission": car_trans,
    "Owner": car_owner,               # new column
    "Location": car_location
})

# SAVE TO CSV
df.to_csv("Cars24_FullData.csv", index=False, encoding="utf-8-sig")
print(df)

# CLOSE DRIVER
driver.quit()
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# set up download dir
download_dir = os.getcwd()

# Chrome options to enable automatic download
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)

print("Accessing page...")

# Initialize driver
driver = webdriver.Chrome(options=options)

# Open the FRED UNRATE page
url = "https://fred.stlouisfed.org/series/UNRATE"
driver.get(url)

# Wait for the download button to appear
wait = WebDriverWait(driver, 15)
download_button = wait.until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="download-button"]')
))
download_button.click()
csv_button = wait.until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="download-data-csv"]')
))
csv_button.click()

print("Downloading file...")

# Wait until download completes
time.sleep(5)
driver.quit()

print(f"Download complete, saveed in current DIR")

# Load the CSV just downloaded
df = pd.read_csv("UNRATE.csv")

# Parse the table
df.rename(columns={'observation_date': 'Date', 'UNRATE': 'Unemployment Rate'}, inplace=True)
df["Date"] = pd.to_datetime(df['Date'])

# Convert to float and drop missing data
df['Unemployment Rate'] = pd.to_numeric(df["Unemployment Rate"], errors='coerce')
df.dropna(inplace=True)
df["6-Month MA"] = df["Unemployment Rate"].rolling(window=6).mean()
print("Summary Statistics:")
print(df["Unemployment Rate"].describe())
print(f"Max: {df['Unemployment Rate'].max()}%")
print(f"Min: {df['Unemployment Rate'].min()}%")
print(f"Mean: {df['Unemployment Rate'].mean():.2f}%")



# plot
sns.set_theme(style='whitegrid')
plt.figure(figsize=(12,6))
plt.axvspan(pd.to_datetime("2007-12-01"), pd.to_datetime("2009-06-01"),
            color="#9ecae1", alpha=0.4, label="2008 Recession", zorder=0)

plt.axvspan(pd.to_datetime("2020-02-01"), pd.to_datetime("2020-04-01"),
            color="#fcbba1", alpha=0.4, label="2020 Recession", zorder=0)
sns.lineplot(data=df, x="Date", y="Unemployment Rate", label="Monthly Rate")
sns.lineplot(data=df, x="Date", y="6-Month MA", label="6-Month MA", linestyle="--")
plt.title('U.S. Unemployment Rate Over Time')
plt.xlabel('Date')
plt.ylabel('Unemployment Rate (%)')
plt.tight_layout()
plt.show()

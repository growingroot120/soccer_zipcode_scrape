import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import csv

# Load the Excel file
excel_path = 'Zip Codes.xlsx'
df = pd.read_excel(excel_path, dtype={'zip': str})

# Initialize the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the website
driver.get('https://nflflag.com/find-league')

# Create and open the CSV file to store results
with open('results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Zip Code", "Link", "League"])

    # Iterate over each zip code in the DataFrame
    for zip_code in df['zip']:
        try:
            # Ensure the zip code is a string with leading zeros if necessary
            zip_code = zip_code.zfill(5)
            
            # Find the input element and enter the zip code
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'form-control.full-height.false.styles_noShowImage__10Eyi'))
            )
            input_element.clear()
            input_element.send_keys(zip_code)

            # Find the specific div containing the radius select element
            parent_div = driver.find_elements(By.CLASS_NAME, 'col-12.col-sm-6.col-md-6.col-xl-2.styles_block__3nuXh')[2]
            
            # Select the radius element within the parent div and set the value to "100 Miles"
            radius_select_element = parent_div.find_element(By.CLASS_NAME, 'styles_radiusSelect__I1hv4.form-control.radius-select')
            select = Select(radius_select_element)
            select.select_by_visible_text("100 Miles")
            
            # Find the search button and click it
            search_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'styles_searchButton__1rf1M.btn.btn-search'))
            )
            search_button.click()
            
            # Wait for the results to load
            time.sleep(2)
            
            # Find the leagues list
            leagues_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'styles_leaguesList__27Kvn'))
            )
            
            # Find all league list items
            league_items = leagues_list.find_elements(By.CLASS_NAME, 'styles_leagueListItem__1DDFG')
            
            # Iterate over each league item and find the desired <a> elements
            for item in league_items:
                try:
                    link_div = item.find_element(By.CLASS_NAME, 'styles_basicLink__2sIjL.styles_linkPartial__1GQrS.styles_linkEmail__3w0jF')
                    a_element = link_div.find_element(By.TAG_NAME, 'a')
                    link_value = a_element.text
                    league_value = item.find_element(By.CLASS_NAME, 'styles_leagueListItemHeader__2PKdn').text
                    # Append result to CSV file
                    writer.writerow([zip_code, link_value, league_value])
                except Exception as e:
                    print(f"Error processing league item for zip code {zip_code}: {e}")
                
        except Exception as e:
            print(f"Error processing zip code {zip_code}: {e}")

# Close the browser
driver.quit()

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

# Load the Excel file
excel_path = 'soccer.xlsx'
df = pd.read_excel(excel_path, dtype={'zip': str})

# Initialize the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the website
driver.get('https://www.aysonational.org/Default.aspx?tabid=961582')

# Create and open the CSV file to store results
with open('results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Zip Code", "Website", "Address", "Email"])

    # Flag to check if dropdown selection has been made
    is_dropdown_selected = False

    # Iterate over each zip code in the DataFrame
    for zip_code in df['zip']:
        try:
            # Ensure the zip code is a string with leading zeros if necessary
            zip_code = zip_code.zfill(5)
            print(zip_code)
            # Find the input element and enter the zip code
            input_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, 'zipCodeTextBox'))
            )
            input_element.clear()
            input_element.send_keys(zip_code)
            time.sleep(1)
            # Select dropdown option "within 50 miles" only for the first zip code
            if not is_dropdown_selected:
                # Wait until the dropdown is present
                dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "distanceDropdown_listbox"))
                )
                    
                # Click on the dropdown to open the options
                dropdown_toggle = driver.find_element(By.CSS_SELECTOR, ".k-dropdown-wrap")
                dropdown_toggle.click()
                    
                # Wait until the options are visible
                options = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#distanceDropdown_listbox li"))
                )
                    
                # Iterate through the options and select the one with text "within 50 miles"
                for option in options:
                    if option.text == "within 50 miles":
                        option.click()
                        break
                
                # Set the flag to True to skip this step for the rest of the zip codes
                is_dropdown_selected = True
            # Find the search button and click it
            header_element = driver.find_element(By.CLASS_NAME, 'ayso-head')
            search_button = header_element.find_element(By.ID, 'searchButton')
            search_button.click()
            time.sleep(1)
            # Find the leagues list
            region_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'locationList'))
            )
            
            # Find all league list items
            region_items = region_list.find_elements(By.CLASS_NAME, 'list')
            
            # Iterate over each league item and find the desired <a> elements
            for item in region_items:
                try:
                    anchor_tag = item. find_element(By.CSS_SELECTOR, 'a.title-link.inline-block')

                    # Get the href attribute value
                    link_value = anchor_tag.get_attribute('href')
                    print(link_value)
                    # Extract the address and email
                    address_div = item.find_element(By.XPATH, ".//div[@data-bind='html: Address']")
                    address_value = address_div.get_attribute('innerHTML').strip()
                    email_div = item.find_element(By.XPATH, ".//div[@data-bind='text: Email']")
                    email_value = email_div.text.strip()                    
                    # Append result to CSV file
                    writer.writerow([zip_code, link_value, address_value, email_value])
                except Exception as e:
                    print(f"Error processing league item for zip code {zip_code}: {e}")
                
        except Exception as e:
            print(f"Error processing zip code {zip_code}: {e}")

# Close the browser
driver.quit()

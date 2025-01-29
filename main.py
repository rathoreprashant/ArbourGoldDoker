from flask import Flask, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import threading

app = Flask(__name__)


DOWNLOAD_DIR = "/tmp/selenium_downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def run_selenium():

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,  # Set download directory
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    })

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://utrees.arborgold.net/AG/#/login")
        time.sleep(3)

        # Check if the login form exists
        try:
            user_name_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/ng-component/div/div[2]/ag-login-form/div[1]/div/form/div/div[2]/div/input"))
            )

            # If found, proceed with login
            user_name_field.send_keys("Lewis")

            password_input = driver.find_element(By.XPATH, "/html/body/app-root/div/ng-component/div/div[2]/ag-login-form/div[1]/div/form/div/div[3]/div/input")
            password_input.send_keys("Hammersport2024!")

            login_btn = driver.find_element(By.XPATH, "/html/body/app-root/div/ng-component/div/div[2]/ag-login-form/div[1]/div/form/div/div[4]/button[1]").click()
            print("Logging in...")
            time.sleep(5)
        except:
            print("Already logged in, skipping login step.")

        # Click the 'Job' menu item
        print("before Job menu...")
        job_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sidenav_link_job"))
        )
        job_menu.click()
        print("Navigated to jobs menu")

        # Click on the filter button to open filter options
        job_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/ag-jobs/div/div/div[2]/div[1]/button[2]/span"))
        )
        job_filter.click()
        print("Opened filter popup")
        time.sleep(3)

        # Select the 'Last Month' option from the dropdown
        period_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/ag-jobs/kendo-popup/div/form/div[2]/div[1]/div/ag-dropdownlist/kendo-dropdownlist/span/span[1]"))
        )
        period_dropdown.click()
        print("Clicked on period dropdown")

        # Click the 'Filter' button
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "jobsFilterButton"))
        )
        filter_button.click()
        print("Clicked on the filter button")
        time.sleep(5)

        # Open export popup and click export
        openExportPopup = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/ag-jobs/div/div/div[2]/div[2]/div[2]/ag-grid-options/div/ag-menu/button/span"))
        )
        openExportPopup.click()
        print("Clicked on the openExportPopup button")

        ExportbTN = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/kendo-popup/div/kendo-menu/ul/li[2]/span/span"))
        )
        ExportbTN.click()
        print("Clicked on the Export button")

        # Wait for the file to download
        time.sleep(5)

        # Get the latest downloaded file
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        if not downloaded_files:
            raise Exception("No files downloaded.")

        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
        print(f"Downloaded file: {latest_file}")

        return latest_file  # File path will be used later to send the file in response

    except Exception as e:
        print(f"Error occurred: {str(e)}")

    finally:
        driver.quit()

@app.route("/download-export")
def download_export(request):
    try:
        # Run selenium in a background thread so Flask does not get blocked
        thread = threading.Thread(target=run_selenium)
        thread.start()
        thread.join()  # Wait for the thread to complete

        # Retrieve the downloaded file once it's available
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        if not downloaded_files:
            raise Exception("No files downloaded.")

        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
        print(f"Returning downloaded file: {latest_file}")

        return send_file(latest_file, as_attachment=True, mimetype='application/octet-stream', attachment_filename=os.path.basename(latest_file))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True , host="0.0.0.0", port=8080)

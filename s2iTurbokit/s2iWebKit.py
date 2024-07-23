##### s2iTurbokit Web module

from .s2iHelperFunctions import getDomainName, getReturnArray, loadJSON, getPrompt, unpackDict2Str, checkPath
from bs4 import BeautifulSoup
from pypdf import PdfWriter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
import re
import pdfkit
import re
import requests
import os
import time  # Add this line to import the time module
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import logging

# Convert a web-page to PDF
def convertWebpageToPDF(webURL):
    """
    Converts a web page to PDF.

    Args:
    - webURL (str): URL of the web page to convert.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (str).
            'status' will be True if successful, False otherwise.
            'message' will contain an error message or success message.
            'data' will contain the path to the generated PDF file if successful.
    """
    try:
        # Get the domain name
        domainName = getDomainName(webURL)

        # Output file name should match the domain name
        if domainName.lower() == "none":
            outFileName = re.sub('[^0-9a-zA-Z]+', '_', webURL) + '_Webpage.pdf'
        else:
            outFileName = domainName.replace(".", "_") + '_Webpage.pdf'
        
        outFilePath = './s2iIO/Out/' + outFileName

        # Convert the web page to PDF. For options see - https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        pdfOptions = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
            "dpi": 300,
            'no-outline': None
        }

        # Perform the conversion and update returnArray based on success or failure
        if pdfkit.from_url(webURL, outFilePath, options=pdfOptions):
            return getReturnArray(True, "Web page successfully converted to PDF", outFilePath)
        else:
            return getReturnArray(False, "Conversion to PDF failed", "")

    except Exception as e:
        error_message = f"An error occurred while converting web page to PDF: {str(e)}"
        return   getReturnArray(False, error_message, "")


def convertWebsiteToPDF(webURL):
    """
    Converts a website and all its sub-pages to a single PDF.

    Args:
    - webURL (str): URL of the website to convert.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (list of dictionaries).
            'status' will be True if successful, False otherwise.
            'message' will contain an error message or success message.
            'data' will contain a list with details of the conversion process if successful.
    """
    try:
        # Initialize returnArray
        returnArray = getReturnArray(True, "", [])

        # URLs of the website. Add the root page as the first page
        urls = [webURL]

        # Get the domain name
        domainName = getDomainName(webURL)
        domain = domainName.rsplit(".")[1]

        # Output file name should match the domain name
        if domainName.lower() == "none":
            outFileName = re.sub('[^0-9a-zA-Z]+', '_', webURL) + '_Website.pdf'
        else:
            outFileName = domainName.replace(".", "_") + '_Website.pdf'
        outFilePath = './s2iIO/Out/' + outFileName

        # Read the main URL
        r = requests.get(webURL)
        s = BeautifulSoup(r.text, "html.parser")

        # Scan all 'href' tags and capture all pages from the URL. No recursion
        for i in s.find_all("a"):
            try:
                href = i.attrs['href'].strip()
                if getDomainName(href) == domainName:
                    if href.endswith('.' + domain) or href.endswith("." + domain + '/'):
                        pass
                    else:
                        urls.append(href)
            except Exception as e:

        # Convert all pages into one PDF using PyPDF2
             merger = PdfWriter()  # Add indentation to fix the expected indented block error
        # Add indented block here
        
        for u in urls:
            pdfkit.from_url(u, 'tmpPDF.pdf')
            with open('tmpPDF.pdf', "rb") as tFile:
                merger.append(tFile)
            
            os.remove('tmpPDF.pdf')

        with open(outFilePath, "wb") as outFile:
            merger.write(outFile)

        # Update returnArray with conversion details
        returnArray["data"].append({
            "numPages": len(urls),
            "fileName": outFilePath,
            "URLs": urls
        })

        return returnArray

    except Exception as e:
        error_message = f"An error occurred while converting website to PDF: {str(e)}"
        return getReturnArray(False, error_message, [])


# Setup the Selenium WebDriver
def setup_driver():
    """
    Set up a Chrome WebDriver instance with headless mode enabled.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (WebDriver instance or None).
            'status' will be True if WebDriver setup was successful, False otherwise.
            'message' will contain an error message if setup failed.
            'data' will contain the WebDriver instance if setup was successful, otherwise None.
    """
    try:
        returnArray = getReturnArray(True, "", None)

        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        service = ChromeService(executable_path='path/to/chromedriver')  # Replace with actual path
        driver = webdriver.Chrome(service=service, options=options)

        returnArray["data"] = driver

    except Exception as e:
        returnArray = getReturnArray(False, str(e), None)

    return returnArray

# Close the Selenium WebDriver
def close_driver(driver):
    """
    Close the provided WebDriver instance.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance to be closed.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if WebDriver was closed successfully, False otherwise.
            'message' will contain an error message if closing failed.
            'data' will always be None.
    """
    try:
        returnArray =getReturnArray(True, "", None)
        
        driver.quit()

    except Exception as e:
        returnArray = getReturnArray(False, str(e), None)

    return returnArray


def navigate_to_url(driver, url):
    """
    Navigate to the specified URL using the provided WebDriver instance.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - url (str): The URL to navigate to.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if navigation was successful, False otherwise.
            'message' will contain an error message if navigation failed.
            'data' will always be None.
    """
    try:
        driver.get(url)
        return getReturnArray(True, "", None)
    
    except Exception as e:
        return getReturnArray(False, str(e), None)



# Wait for the presence of an element located by a specific method within a timeout period
def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for the presence of an element located by a specific method within a timeout period.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).
    - timeout (int): Timeout period in seconds (default is 10 seconds).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (WebElement or None).
            'status' will be True if the element is located within the timeout, False otherwise.
            'message' will contain an error message if the element could not be located.
            'data' will be the located WebElement if successful, or None if not found.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        # Wait for the presence of the element
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        returnArray["data"] = element  # Update return array with located element
    except TimeoutException:
        returnArray = getReturnArray(False, f"Timeout waiting for element with {by}={value}", None)
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while waiting for element: {str(e)}", None)

    return returnArray



# Extract and return the text content of an element located by a specific method
def extract_text(driver, by, value):
    """
    Extracts the text content of an element located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (str or None).
            'status' will be True if text extraction is successful, False otherwise.
            'message' will contain an error message if extraction fails.
            'data' will be the extracted text if successful, or None if an error occurs.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        element = driver.find_element(by, value)
        text = element.text.strip()
        returnArray["data"] = text  # Update return array with extracted text
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while extracting text: {str(e)}", None)

    return returnArray



# Extract and return the value of a specified attribute from an element located by a specific method
def extract_attribute(driver, by, value, attribute):
    """
    Extracts the value of a specified attribute from an element located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).
    - attribute (str): The name of the attribute whose value needs to be extracted.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (str or None).
            'status' will be True if attribute extraction is successful, False otherwise.
            'message' will contain an error message if extraction fails.
            'data' will be the attribute's value if successful, or None if an error occurs.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        element = driver.find_element(by, value)
        attr_value = element.get_attribute(attribute)
        returnArray["data"] = attr_value  # Update return array with attribute value
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except Exception as e:
        returnArray =getReturnArray(False, f"Error occurred while extracting attribute: {str(e)}", None)

    return returnArray



# Click on an element located by a specific method
def click_element(driver, by, value):
    """
    Clicks on an element located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if the click operation is successful, False otherwise.
            'message' will contain an error message if clicking fails.
            'data' will be None.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        element = driver.find_element(by, value)
        element.click()
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except ElementClickInterceptedException:
        returnArray = getReturnArray(False, f"Element {by}={value} is not clickable at the moment", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while clicking element: {str(e)}", None)

    return returnArray



# Send keys to an input field element located by a specific method
def send_keys_to_element(driver, by, value, keys):
    """
    Sends keys to an element located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).
    - keys (str): The keys to be sent to the element (e.g., input text).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if sending keys is successful, False otherwise.
            'message' will contain an error message if sending keys fails.
            'data' will be None.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        element = driver.find_element(by, value)
        element.send_keys(keys)
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except ElementNotInteractableException:
        returnArray = getReturnArray(False, f"Element {by}={value} is not interactable at the moment", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while sending keys to element: {str(e)}", None)

    return returnArray


# Extract and return a list of elements located by a specific method
def extract_multiple_elements(driver, by, value):
    """
    Extracts multiple elements located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the elements (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (list).
            'status' will be True if extraction is successful, False otherwise.
            'message' will contain an error message if extraction fails.
            'data' will contain a list of WebElement objects if extraction is successful, otherwise None.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        elements = driver.find_elements(by, value)
        returnArray.update({"data": elements})
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Elements not found with {by}={value}", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while extracting elements: {str(e)}", None)

    return returnArray


# Scroll to an element located by a specific method on the webpage
def scroll_to_element(driver, by, value):
    """
    Scrolls to an element located by a specific method.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - by (selenium.webdriver.common.by.By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
    - value (str): The value used by the locating method (e.g., XPath expression, element ID, etc.).

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if scrolling is successful, False otherwise.
            'message' will contain an error message if scrolling fails.
            'data' will be None.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        element = driver.find_element(by, value)
        driver.execute_script("arguments[0].scrollIntoView();", element)
    except NoSuchElementException:
        returnArray = getReturnArray(False, f"Element not found with {by}={value}", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while scrolling to element: {str(e)}", None)

    return returnArray


# Handle popups or alerts that appear on the webpage
def handle_alert(driver, action='accept'):
    """
    Handles browser alerts by accepting or dismissing them.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - action (str): Action to perform on the alert. Valid values: 'accept' (default), 'dismiss'.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
            'status' will be True if alert handling is successful, False otherwise.
            'message' will contain an error message if handling fails.
            'data' will be None.
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        if action == 'accept':
            alert.accept()
        elif action == 'dismiss':
            alert.dismiss()
        else:
            returnArray = getReturnArray(False, f"Invalid action '{action}' specified for handling alert", None)
    except TimeoutException:
        returnArray = getReturnArray(False, "No alert present to handle", None)
    except Exception as e:
        returnArray = getReturnArray(False, f"Error occurred while handling alert: {str(e)}", None)

    return returnArray


def chrome_headless():
    """
    Returns a headless Chrome browser instance.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (headless Chrome WebDriver instance).
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument("--proxy-bypass-list=*")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-blink-features=BlockCredentialedSubresources")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        # Set up the WebDriver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        returnArray["data"] = driver
    except Exception as e:
        returnArray =getReturnArray(False, f"Error setting up headless Chrome WebDriver: {str(e)}", None)

    return returnArray



def initialize_webdriver():
    """
    Initializes a WebDriver instance for Chrome and maximizes the window.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (initialized Chrome WebDriver instance with maximized window).
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        # Set up Chrome options if needed
        chrome_options = Options()
        # Add any Chrome options if required
        # For example:
        # chrome_options.add_argument("--headless")  # Uncomment to run headless
        
        # Initialize the WebDriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()  # Maximize the browser window
        returnArray["data"] = driver
    except Exception as e:
        returnArray = getReturnArray(False, f"Error initializing Chrome WebDriver: {str(e)}", None)

    return returnArray


def scrape_url(driver, url):
    """
    Navigates the WebDriver to the specified URL and maximizes the window.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    url (str): URL to navigate to.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        # Navigate to the specified URL
        driver.get(url)
        # Maximize the browser window
        driver.maximize_window()
    except Exception as e:
        returnArray = getReturnArray(False, f"Error navigating to URL '{url}': {str(e)}", None)

    return returnArray



def close_overlays(driver):
    """
    Attempts to close overlays or pop-ups if they exist on the current page.

    Args:
    driver (WebDriver): Initialized WebDriver instance.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (None).
    """
    returnArray = getReturnArray(True, "", None)  # Initialize return array

    try:
        # Example selector for a common overlay
        overlay = driver.find_element(By.CSS_SELECTOR, 'div.overlay-class')  # Update selector based on actual overlay class
        if overlay:
            close_button = overlay.find_element(By.CSS_SELECTOR, 'button.close')
            if close_button:
                close_button.click()
                time.sleep(1)  # Give some time for the overlay to close
    except NoSuchElementException:
        returnArray.update({"message": "No overlay found"})
    except Exception as e:
        returnArray = getReturnArray(False, f"Error closing overlay: {str(e)}", None)

    return returnArray



def click_element_multiple_retries(driver, element, retries=3):
    """
    Attempts to click an element multiple times with retries.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    element (WebElement): Element to be clicked.
    retries (int): Number of retries in case of failure. Default is 3.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (True if successful, False otherwise).
    """
    try:
        for attempt in range(retries):
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
                ActionChains(driver).move_to_element(element).click().perform()
                return getReturnArray(True, "", True)
            except (ElementClickInterceptedException, TimeoutException) as e:
                time.sleep(attempt + 1)  # Increase delay on each retry
                if attempt == retries - 1:
                    return getReturnArray(False, str(e), False)
    except Exception as e:
        return getReturnArray(False, str(e), None)

    return getReturnArray(False, "Unknown error occurred", False)


def find_elements(driver, xpath):
    """
    Finds elements on the page based on the given XPath.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath expression to locate elements.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (list of found elements or empty list on error).
    """
    try:
        wait = WebDriverWait(driver, 20)
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        return getReturnArray(True, "", elements)
    except Exception as e:

        return getReturnArray(False, str(e), [])
    



# Navigate through pagination and scrape data from multiple pages
def scrape_multiple_pages(driver, start_url, pagination_locator):
    """
    Scrapes data from multiple pages using pagination.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    start_url (str): URL of the starting page.
    pagination_locator (tuple): Locator (By, value) of the next page button.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (list of scraped data).
    """
    returnArray = getReturnArray(True, "", [])

    try:
        current_url = start_url
        while True:
            driver.get(current_url)

            # Scrape data from the current page (example function)
            data_on_page = scrape_data_from_current_page(driver)
            if not data_on_page["status"]:
                raise Exception("Error scraping data from the current page")

            # Append scraped data to the result list
            returnArray["data"].extend(data_on_page["data"])

            # Check if there is a next page and navigate to it
            next_button = driver.find_element(*pagination_locator)
            if not next_button.is_enabled():
                break  # No more pages available, exit loop

            next_button.click()
            current_url = driver.current_url

        returnArray["message"] = "Pagination completed successfully"
    except Exception as e:
        returnArray = getReturnArray(False, str(e), [])

    return returnArray


# Example function to scrape data from the current page
def scrape_data_from_current_page(driver):
    """
    Scrapes data from the current page using WebDriver.

    Args:
    driver (WebDriver): Initialized WebDriver instance.

    Returns:
    dict: A dictionary containing 'status' (bool), 'message' (str), and 'data' (list of scraped data).
    """
    returnArray = getReturnArray(True, "", [])

    try:
        # Example: Find elements on the page and extract data
        elements = driver.find_elements(By.XPATH, '//div[@class="result-item"]')
        for element in elements:
            # Extract data from each element and append to result list
            item_data = {
                "title": element.find_element(By.XPATH, './h2').text,
                "description": element.find_element(By.XPATH, './p').text
            }
            returnArray["data"].append(item_data)
    except Exception as e:
        returnArray = getReturnArray(False, str(e), [])

    return returnArray

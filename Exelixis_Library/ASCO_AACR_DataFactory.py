import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException,NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.common.by import By
import pandas as pd 
from bs4 import BeautifulSoup
from s2iTurbokit.s2iHelperFunctions import getReturnArray
from s2iExtensions.Exelixis.AACRConfig import WEBSITE_CONFIG
from logging import getLogger
import re

def initialize_combined_data():
    """
    Initializes a dictionary with empty lists for storing combined event data.
 
    Returns:
    dict: Dictionary with keys for different event attributes and empty lists as values.
          Keys:
          - 'Event Type': List of event types.
          - 'Date': List of dates.
          - 'Time': List of times.
          - 'Start Time': List of start times.
          - 'End Time': List of end times.
          - 'Time Zone': List of time zones.
          - 'Location': List of locations.
          - 'Session Type': List of session types.
          - 'Session Details': List of session details.
          - 'Title': List of titles.
          - 'Abs': List of abstracts.
          - 'Disease': List of diseases.
          - 'Authors': List of authors.
          - 'Affiliations': List of affiliations.
          - 'Source': List of sources.
    """
    combined_data = {
        "Event Type": [],
        "Date": [],
        "Time": [],
        "Start Time": [],
        "End Time": [],
        "Time Zone": [],
        "Location": [],
        "Session Type": [],
        "Session Details": [],
        "Title": [],
        "Abs": [],
        "Disease": [],
        "Authors": [],
        "Affiliations": [],
        "Details": [],
        "Source": []
    }
 
    presentation_variables = {
        "presentation_link_text": "",
        "custom_name_with_link": "",
        "presentation_link_text_values": "",
        "presentation_link_text_value": ""
    }
    return combined_data


def convert_mutiple_dateformats(driver, xpath):
    """
    Converts website time format into structured date, start time, end time, and timezone.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str or list): XPath to locate elements or list of WebElement elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of dictionaries with structured time information).
    """
    try:
        if isinstance(xpath, str):
            elements = driver.find_elements(By.XPATH, xpath)
        elif isinstance(xpath, list):
            elements = xpath
        else:
            return getReturnArray(False, "Invalid type for xpath", [])

        if not elements:
            return getReturnArray(False, f"No elements found using XPath: {xpath}", [])

        date_time_text = []
        for element in elements:
            text = element.text.strip()
            parts = text.split()

            try:
                # Check for Format 1: "31 May 2024 13:00 – 14:15 GMT-5"
                if len(parts) >= 9 and parts[-1].startswith(('PST', 'GMT', 'CDT')):
                    date = parts[1].strip(',') + "-" + parts[0] + "-" + parts[2]
                    start_time = parts[3] + " " + parts[4]
                    end_time = parts[6] + " " + parts[7]
                    timezone = parts[8]
                    time = start_time + "-" + end_time

                # Check for Format 2: "2024-05-31 13:00 – 14:15"
                elif len(parts) >= 5 and parts[1].count('-') == 2 and parts[2].count(':') == 2:
                    date = parts[1]
                    start_time = parts[2]
                    end_time = parts[4]
                    timezone = None
                    time = start_time + "-" + end_time

                # Check for New Format: "April 7, 2024, 1:30 PM - 5:00 PM"
                elif len(parts) >= 7 and ',' in parts[1]:
                    month_day_year = parts[1].strip(',')
                    date = month_day_year.replace(',', '-') + "-" + parts[0]
                    start_time = parts[3] + " " + parts[4]
                    end_time = parts[6] + " " + parts[7]
                    timezone = None
                    time = start_time + "-" + end_time

                else:
                    raise ValueError("Unrecognized format")

                date_time_text.append({
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'timezone': timezone,
                    'time': time
                })
            except Exception as e:
                date_time_text.append({
                    'original_text': text  # Include original text if structured data cannot be parsed
                })

        return getReturnArray(True, "Time extraction successful", date_time_text)

    except NoSuchElementException:
        return getReturnArray(False, f"Element not found using XPath: {xpath}", [])
    except Exception as e:
        # Log any errors that occur during extraction
        return getReturnArray(False, f"Error while extracting time: {e}", [])
    

def extract_locations(driver, xpath):
    """
    Extracts location information from elements found by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate location elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of location texts extracted from elements, or None if there's an error).
    """
    try:
        if not xpath:
            return getReturnArray(False, "No location XPath provided", None)
       
        # Wait for all location elements to be present
        locations = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        location_texts = [location_element.text.strip().replace("Location", "").strip() for location_element in locations]
       
        return getReturnArray(True, "Locations extracted successfully", location_texts)
       
    except TimeoutException as te:
        return getReturnArray(False, f"Timeout while locating location elements: {te}", None)
    except Exception as e:
        return getReturnArray(False, f"Error while extracting locations: {e}", None)
    

def extract_event_type(driver, xpath):
    """
    Extracts event types from elements found by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate event type elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of event types extracted from elements, or empty list if not found or on error).
    """
    try:
        event_type_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        event_types = [event_type_element.text.strip() for event_type_element in event_type_elements]
        return getReturnArray(True, "Event types extracted successfully", event_types)
   
    except NoSuchElementException:
        return getReturnArray(False, "Event type elements not found", [])
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating event type elements", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting event type: {e}", [])
    

def extract_session_type(driver, xpath):
    """
    Extracts session types from elements found by XPath.
 
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate session type elements.
 
    Returns:
    list: List of session types extracted from elements, or empty list if not found or on error.
    """
    try:
        session_type_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        session_types = [session_type_element.text.strip() for session_type_element in session_type_elements]
        return getReturnArray(True, "Session types extracted successfully", session_types)
        
    except NoSuchElementException:
        return getReturnArray(False, "Session type elements not found", [])
  
    except TimeoutException as e:
        return getReturnArray(False, f"Timeout while locating session type elements: {e}", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting session type: {e}", [])


def extract_disease(driver, xpath):
    """
    Extracts disease information from elements found by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate disease elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of diseases extracted from elements, or empty list if not found or on error).
    """
    try:
        disease_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        diseases = [disease_element.text.strip().replace("Track", "").strip() for disease_element in disease_elements]
        return getReturnArray(True, "Diseases extracted successfully", diseases)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating disease elements", [])
    except NoSuchElementException:
        return getReturnArray(False, "Disease elements not found", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting disease: {e}", [])
    
    
def extract_presentation_time(driver, xpath):
    """
    Extracts presentation time information from elements found by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate presentation time elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of dictionaries with presentation time details,
          or empty list if not found or on error).
    """
    try:
        presentation_time_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        presentation_times = []
        
        for presentation_time_element in presentation_time_elements:
            presentation_time_text = presentation_time_element.text.strip()
            pattern = r'(\d{1,2}:\d{2} [AP]M) – (\d{1,2}:\d{2} [AP]M) (PST|GMT|CDT)'
            matches = re.search(pattern, presentation_time_text)
            
            if matches:
                p_start_time = matches.group(1)
                p_end_time = matches.group(2)
                p_time_zone = matches.group(3)
                p_time = f"{p_start_time} - {p_end_time}"
            else:
                p_time = "No Time"
                p_start_time = "No Time"
                p_end_time = "No Time"
                p_time_zone = "No Time Zone"
            
            presentation_times.append({
                'p_time': p_time,
                'p_start_time': p_start_time,
                'p_end_time': p_end_time,
                'p_time_zone': p_time_zone
            })
        return getReturnArray(True, "Presentation times extracted successfully", presentation_times)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation time elements", [])
    except NoSuchElementException:
        return getReturnArray(False, "Presentation time elements not found", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting presentation time: {e}", [])
    

def extract_session_authors(driver, xpath):
    """
    Extracts session authors from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate session authors.
    
    Returns:
    dict: Dictionary containing status, message, and data (semi-colon separated string of session authors' names,
          or empty list if not found or on error).
    """
    try:
        session_authors_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        
        session_authors = '; '.join([author.text.strip() for author in session_authors_elements])
        return getReturnArray(True, "Session authors extracted successfully", session_authors)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while extracting session authors", "")
    except NoSuchElementException:
        return getReturnArray(False, "Session authors elements not found", "")
    except Exception as e:
        return getReturnArray(False, f"Error extracting session authors: {e}", "")
    

def extract_session_authors_affiliations(driver, xpath):
    """
    Extracts session authors' affiliations from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate session authors' affiliations.
    
    Returns:
    dict: Dictionary containing status, message, and data (semi-colon separated string of session authors' affiliations,
          or empty list if not found or on error).
    """
    try:
        session_authors_affiliations_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        
        session_authors_affiliations = '; '.join([affiliation.text.strip() for affiliation in session_authors_affiliations_elements])
        return getReturnArray(True, "Session authors' affiliations extracted successfully", session_authors_affiliations)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while extracting session authors' affiliations", "")
    except NoSuchElementException:
        return getReturnArray(False, "Session authors' affiliations elements not found", "")
    except Exception as e:
        return getReturnArray(False, f"Error extracting session authors' affiliations: {e}", "")


# Add the corrected extract_presentation_titles function here

def extract_presentation_titles(driver, xpath):
    """
    Extracts presentation titles from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate presentation titles.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of presentation titles,
          or empty list if not found or on error).
    """
    presentation_titles = []
    
    try:
        extract_presentation_section = WEBSITE_CONFIG['asco'].get('presentation_section')
        presentation_sections = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, extract_presentation_section)))
        
        for section in presentation_sections:
            try:
                # Get Presentation Title
                presentation_title = section.find_element(By.XPATH, xpath).text.strip()
                presentation_titles.append(presentation_title)
                
            except NoSuchElementException as e:
               return getReturnArray(False, f"No presentation titles found using XPath: {xpath}", [])
            except Exception as e:
            
               return getReturnArray(False, f"Error while extracting presentation titles: {e}", [])
            
        return getReturnArray(True, "Presentation titles extracted successfully", presentation_titles)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation sections", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting presentation titles: {e}", [])
 
 
 

def extract_presentation_authors(driver, xpath):
    """
    Extracts presentation authors from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate presentation authors.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of strings representing authors for each presentation,
          or empty list if not found or on error).
    """
    authors_list = []
    
    try:
        # Get the XPath for the presentation section from configuration
        extract_presentation_section = WEBSITE_CONFIG['asco'].get('presentation_section')
        if not extract_presentation_section:

            return getReturnArray(False, "Presentation section XPath not configured", [])
 
        # Locate all presentation sections
        presentation_sections = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, extract_presentation_section)))
       
        for section in presentation_sections:
            try:
                # Get Authors
                authors = section.find_elements(By.XPATH, xpath)

                if not authors:
                    raise NoSuchElementException(f"No presentation authors found using XPath: {xpath}")
               
                # Ensure each author's text is a string
                authors_text = ';'.join([str(author.text).strip() for author in authors if author.text.strip()])
                if not authors_text:
                    authors_text = "No authors found"
 
                authors_list.append(authors_text)
               
            except NoSuchElementException as e:
                authors_list.append("No authors found")
            except Exception as e:
                authors_list.append(f"Error: {str(e)}")
       
        return getReturnArray(True, "Presentation authors extracted successfully", authors_list)
   
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation sections", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting presentation authors: {e}", [])
    
    

def extract_presentation_affiliations(driver, xpath):
    """
    Extracts presentation affiliations from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate presentation affiliations.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of strings representing affiliations for each presentation,
          or empty list if not found or on error).
    """
    affiliations_list = []
    
    try:
        extract_presentation_section = WEBSITE_CONFIG['asco'].get('presentation_section')
        if not extract_presentation_section:
            return getReturnArray(False, "Presentation section XPath not configured", [])
 
        presentation_sections = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, extract_presentation_section)))
       
        for section in presentation_sections:
            try:
                # Get Affiliations
                affiliations = section.find_elements(By.XPATH, xpath)
                if not affiliations:
                    raise NoSuchElementException("No presentation affiliations found using XPath: {xpath}")
       
                affiliations_text = ';'.join([affiliation.text.strip() for affiliation in affiliations])
                affiliations_list.append(affiliations_text)
 
            except NoSuchElementException as e:
                affiliations_list.append("No affiliations found")
            except Exception as e:
                affiliations_list.append(f"Error: {str(e)}")
       
        return getReturnArray(True, "Presentation affiliations extracted successfully", affiliations_list)
   
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation sections", [])
    except Exception as e:
        return getReturnArray(False, f"Error while extracting presentation affiliations: {e}", [])
    

def get_presentationLink(driver, xpath):
    """
    Extracts presentation link and associated text from elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate the presentation links.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of dictionaries containing presentation link text values and texts,
          or a list with one dictionary with "No Presentations" if not found).
    """
    try:
        presentation_link_elements = driver.find_elements(By.XPATH, xpath)
        if not presentation_link_elements:
            return getReturnArray(True, "No presentations found", [{
                'presentation_link_text_value': "No Presentations",
                'presentation_link_text': "No Presentations"
            }])
       
        presentation_links = []
        for element in presentation_link_elements:
            presentation_link_text_value = element.get_attribute('href')
            link_text = element.text.strip()
            presentation_link_text = f'=HYPERLINK("{presentation_link_text_value}", "{link_text}")'
            presentation_links.append({
                'presentation_link_text_value': presentation_link_text_value,
                'presentation_link_text': presentation_link_text
            })
       
        return getReturnArray(True, "Presentation links extracted successfully", presentation_links)
 
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation link element", [{
            'presentation_link_text_value': "No Presentations",
            'presentation_link_text': "No Presentations"
        }])
    except Exception as e:
        return getReturnArray(False, f"Error extracting presentation link: {e}", [{
            'presentation_link_text_value': "No Presentations",
            'presentation_link_text': "No Presentations"
        }])


def get_Presentation_title_elements(driver, xpath):
    """
    Retrieves presentation title elements located by XPath.
    
    Args:
    driver (WebDriver): Initialized WebDriver instance.
    xpath (str): XPath to locate presentation title elements.
    
    Returns:
    dict: Dictionary containing status, message, and data (list of WebDriver elements representing presentation titles,
          or an empty list if no elements found or on error).
    """
    try:
        presentation_title_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        titles = []
        for presentation_title_element in presentation_title_elements:
            presentation_title = presentation_title_element.text.strip()
            titles.append(presentation_title)
        
        return getReturnArray(True, "Presentation titles extracted successfully", titles)
    
    except TimeoutException:
        return getReturnArray(False, "Timeout while locating presentation title elements", [])
    except Exception as e:
        return getReturnArray(False, f"Error extracting presentation title elements: {e}", [])
    

def extract_presentation_authors_affiliations(driver, authors_xpath, abstract_xpath):
    """
    Extracts presentation authors, affiliations, and abstract from elements located by XPath.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    authors_xpath (str): XPath to locate authors element.
    abstract_xpath (str): XPath to locate abstract element.

    Returns:
    dict: Dictionary containing status, message, and data (DataFrame with authors, affiliations, and abstract,
          or None if extraction fails).
    """
    try:
        # Wait until the authors element is present
        authors_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, authors_xpath))
        )
        authors_html = authors_element.get_attribute('innerHTML').strip()

        # Split authors and affiliations using possible delimiters
        parts = re.split(r'<br\s*/?>\s*<br\s*/?>|;\s*<br\s*/?>', authors_html, flags=re.I)

        # Ensure we have at least two parts (authors and affiliations)
        if len(parts) < 2:
            raise ValueError("Expected at least two parts (authors and affiliations) in the HTML content")

        authors_part = parts[0].strip()
        affiliations_part = parts[1].strip()

        # Extract authors and their numbers without HTML tags
        authors_soup = BeautifulSoup(authors_part, "html.parser")
        authors_text = authors_soup.get_text(separator=" ")
        authors_with_sup = re.findall(r'(.*?)\s*(\d+)', authors_text)
        if not authors_with_sup:
            authors_list = re.split(r',\s*', authors_text)
            authors_with_sup = [(author.strip(), '') for author in authors_list]

        # Extract affiliations
        affiliations_soup = BeautifulSoup(affiliations_part, "html.parser")
        affiliations_text = affiliations_soup.get_text(separator="; ")
        affiliations_list = re.split(r'(\d+)\s*;', affiliations_text)

        # Remove empty strings from affiliations list
        affiliations_list = [affiliation.strip() for affiliation in affiliations_list if affiliation.strip()]

        # Combine authors and their respective numbers correctly
        authors_cleaned = [f"{name.strip()} {number.strip()}" for name, number in authors_with_sup]

        # Combine affiliations correctly
        affiliations_cleaned = []
        for i in range(0, len(affiliations_list), 2):
            number = affiliations_list[i]
            name = affiliations_list[i + 1] if (i + 1) < len(affiliations_list) else ''
            affiliations_cleaned.append(f"{number} {name.strip()}")

        if not any(number for name, number in authors_with_sup):
            affiliations_cleaned = [f"{affiliations_part}"]

        # Extract the abstract
        abstract_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, abstract_xpath))
        )
        abstract_html = abstract_element.get_attribute('innerHTML').strip()
        abstract_soup = BeautifulSoup(abstract_html, "html.parser")
        abstract_text = abstract_soup.get_text(separator=" ", strip=True)

        # Create a DataFrame with authors, affiliations, and abstract
        authors_str = '; '.join(authors_cleaned).replace(", ;", ";").replace("; ,", ";").replace("; ", ";").strip(",; ")
        affiliations_str = '; '.join(affiliations_cleaned).replace(", ;", ";").replace("; ,", ";").replace(";;", ";").strip(",; ")
        abstract_str = abstract_text

        p_df = pd.DataFrame({
            'Authors': [authors_str],
            'Affiliations': [affiliations_str],
            'Abstract': [abstract_str]
        })

        return getReturnArray(True, "Successfully extracted presentation data", p_df)

    except TimeoutException as te:
        return getReturnArray(False, f"Timeout waiting for element: {te}", None)

    except NoSuchElementException as nse:
        return getReturnArray(False, f"Element not found: {nse}", None)

    except ValueError as ve:
        return getReturnArray(False, f"ValueError: {ve}", None)

    except Exception as e:
        driver.save_screenshot("error_screenshot.png")  # Save a screenshot for debugging
        return getReturnArray(False, f"An error occurred: {e}", None)


def navigate_back(driver):
    """
    Navigate back to the previous page using the provided XPath.

    Args:
    driver (WebDriver): Initialized WebDriver instance.
    """
    try:
        navigate_back_xpath = config.WEBSITE_CONFIG['website2'].get('navigate_back')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, navigate_back_xpath))
        ).click()
        return getReturnArray(True, "Successfully navigated back to the previous page", None)

    except TimeoutException as te:
        return getReturnArray(False, f"Timeout waiting for navigation element: {te}", None)

    except NoSuchElementException as nse:
        return getReturnArray(False, f"Navigation element not found: {nse}", None)

    except Exception as e:
        driver.save_screenshot("error_screenshot.png")  # Save a screenshot for debugging
        return getReturnArray(False, f"An error occurred during navigation: {e}", None)


def get_element_text(driver, xpath):
    """
    Retrieve the text of an element identified by XPath.

    Args:
    - driver (WebDriver): The Selenium WebDriver instance.
    - xpath (str): XPath expression to locate the element.

    Returns:
    - dict: Dictionary containing 'status' (bool), 'message' (str), and 'data' (str).
            'status' will be True if successful, False otherwise.
            'message' will contain an error message or success message.
            'data' will contain the text content of the located element, or an empty string if element is not found.
    """
    try:
        # Wait up to 10 seconds for the element to be present in the DOM
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element_text = element.text.strip()  # Get the text and strip any leading/trailing whitespace
        return getReturnArray(True, "Successfully retrieved element text", element_text)

    except TimeoutException:
        error_message = f"Timeout while waiting for element with XPath: {xpath}"
        logger.error(error_message)
        return getReturnArray(False, error_message, "")

    except Exception as e:
        error_message = f"Exception occurred while retrieving element text: {str(e)}"
        logger.error(error_message)
        return getReturnArray(False, error_message, "")

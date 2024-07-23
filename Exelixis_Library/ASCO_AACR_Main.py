# Module1/some_module1_script.py
import sys
import os
import logging
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Exelixis_Library.ASCO_AACR_DataFactory import initialize_combined_data, extract_event_type, convert_mutiple_dateformats, extract_session_type, extract_locations, extract_disease, extract_session_authors, extract_session_authors_affiliations, get_Presentation_title_elements, extract_presentation_titles,extract_presentation_authors,extract_presentation_affiliations,extract_presentation_time
from s2iTurbokit.s2iHelperFunctions import getDomainName, getReturnArray, loadJSON, getPrompt, unpackDict2Str, checkPath
from s2iTurbokit.s2iWebKit import initialize_webdriver, scrape_url, find_elements, click_element_multiple_retries
from s2iExtensions.Exelixis.AACRConfig import WEBSITE_CONFIG

def main():
    combined_data = initialize_combined_data()

    try:
        logger.info("Starting the web scraping script...")

        result = initialize_webdriver()
        if not result["status"]:
            logger.error(result["message"])
            return
        driver = result["data"]

        url = WEBSITE_CONFIG['asco']['url']
        logger.info(f"Navigating to URL: {url}")
        scrape_url(driver, url)

        elements_result = find_elements(driver, WEBSITE_CONFIG['asco']['findelements'])
        if not elements_result["status"]:
            logger.error(elements_result["message"])
            return
        elements = elements_result["data"]

        logger.info(f"Number of elements found: {len(elements)}")
        for index in range(0, 2):
            try:
                logger.info(f"Processing element at index: {index}")
                elements_result = find_elements(driver, WEBSITE_CONFIG['asco']['findelements'])
                if not elements_result["status"]:
                    logger.error(elements_result["message"])
                    continue
                elements = elements_result["data"]

                if index < len(elements):
                    driver.execute_script("arguments[0].scrollIntoView();", elements[index])
                    ActionChains(driver).move_to_element(elements[index]).perform()

                    if not click_element_multiple_retries(driver, elements[index]):
                        continue
                time.sleep(WEBSITE_CONFIG['asco']['sleep_duration'])

                session_event_type_result = extract_event_type(driver, WEBSITE_CONFIG['asco'].get('event_type'))
                if session_event_type_result["status"]:
                    event_types = session_event_type_result["data"]
                    if event_types:
                        session_event_type = event_types[0]
                        logger.info(f"Event Type: {session_event_type}")
                    else:
                        logger.error("No Event Type found.")
                else:
                    logger.error(session_event_type_result["message"])

                session_date_time_elements_result = find_elements(driver, WEBSITE_CONFIG['asco'].get('dateandtime_element'))
                if not session_date_time_elements_result["status"]:
                    logger.error(session_date_time_elements_result["message"])
                    continue
                session_date_time_elements = session_date_time_elements_result["data"]

                session_time_parts_result = convert_mutiple_dateformats(driver, session_date_time_elements)
                if session_time_parts_result["status"]:
                    session_time_parts = session_time_parts_result["data"]
                    for part in session_time_parts:
                        session_date = part.get('date', '')
                        session_start_time = part.get('start_time', '')
                        session_end_time = part.get('end_time', '')
                        session_timezone = part.get('timezone', '')
                        session_full_time = part.get('time', '')
                        session_title_xpath = WEBSITE_CONFIG['asco'].get('title_element')
                        session_title_element_txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, session_title_xpath))).text.strip() if session_title_xpath else ""

                        session_types = WEBSITE_CONFIG['asco'].get('session_types')
                        session_type_element = extract_session_type(driver, session_types)
                        if session_type_element["status"]:
                            session_type_elements = session_type_element["data"]
                            if session_type_elements:
                                session_type_element = session_type_elements
                            else:
                                logger.error("No session types found.")

                        session_location_xpath = WEBSITE_CONFIG['asco'].get('location')
                        session_location_texts = extract_locations(driver, session_location_xpath) if session_location_xpath else []
                        if session_location_texts["status"]:
                            session_location_text = session_location_texts["data"]
                            if session_location_text:
                                session_location_text = session_location_text
                            else:
                                logger.error("No session locations found.")

                        session_details_text = f"{session_type_elements};{';'.join(session_location_text)};{session_title_element_txt}"

                        session_disease_xpath = WEBSITE_CONFIG['asco'].get('disease')
                        session_diseases = extract_disease(driver, session_disease_xpath) if session_disease_xpath else []
                        if session_diseases["status"]:
                            session_diseases = session_diseases["data"]
                            if session_diseases:
                                session_diseases = session_diseases[0]
                            else:
                                logger.error("No diseases found.")

                        session_authors_xpath = WEBSITE_CONFIG['asco'].get('session_authors_xpath')
                        session_authors = extract_session_authors(driver, session_authors_xpath) if session_authors_xpath else []
                        if session_authors["status"]:
                            session_authors = session_authors["data"]
                            if session_authors:
                                session_authors = session_authors[0]
                            else:
                                logger.error("No session authors found.")

                        session_authors_affiliations_xpath = WEBSITE_CONFIG['asco'].get('session_authors_affiliations_xpath')
                        session_authors_affiliations = extract_session_authors_affiliations(driver, session_authors_affiliations_xpath) if session_authors_affiliations_xpath else []
                        if session_authors_affiliations["status"]:
                            session_authors_affiliations = session_authors_affiliations["data"]
                            if session_authors_affiliations:
                                session_authors_affiliations = session_authors_affiliations[0]
                            else:
                                logger.error("No session authors affiliations found.")

                        custom_name_with_link = f'=HYPERLINK("{driver.current_url}", "{session_type_elements}")'

                        presentation_link_text_values = driver.current_url

                        # Append session data to combined_data dictionary
                        combined_data["Event Type"].append(session_event_type)
                        combined_data["Date"].append(session_date)
                        combined_data["Time"].append(session_full_time)
                        combined_data["Start Time"].append(session_start_time)
                        combined_data["End Time"].append(session_end_time)
                        combined_data["Time Zone"].append(session_timezone)
                        combined_data["Location"].append(";".join(session_location_text))
                        combined_data["Session Type"].append(session_type_elements)
                        combined_data["Session Details"].append(session_details_text)
                        combined_data["Title"].append(session_title_element_txt)
                        combined_data["Abs"].append(custom_name_with_link)
                        combined_data["Disease"].append(session_diseases)
                        combined_data["Authors"].append(session_authors)
                        combined_data["Affiliations"].append(session_authors_affiliations)
                        combined_data["Details"].append("No Details Found")
                        combined_data["Source"].append(presentation_link_text_values)

                        presentation_title_xpath = WEBSITE_CONFIG['asco'].get('presentation_title')
                        presentation_titles = extract_presentation_titles(driver, presentation_title_xpath) if presentation_title_xpath else []

                        if presentation_titles["status"]:
                            presentation_titles = presentation_titles["data"]
                            if presentation_titles:
                                presentation_titles = presentation_titles
                                print(type(presentation_titles))
                            else:
                                logger.error("No presentation titles found.")


                        presentation_authors_xpath =WEBSITE_CONFIG['asco'].get('presentation_authors')
                        presentation_authors = extract_presentation_authors(driver, presentation_authors_xpath) if presentation_authors_xpath else []
                        if presentation_authors["status"]:
                            presentation_authors = presentation_authors["data"]
                            if presentation_authors:
                                presentation_authors = presentation_authors
                                print(presentation_authors)
                            else:
                                logger.error("No presentation authors found.")


                        presentation_affiliations_xpath = WEBSITE_CONFIG['asco'].get('presentation_affiliations')
                        presentation_affiliations = extract_presentation_affiliations(driver, presentation_affiliations_xpath) if presentation_affiliations_xpath else []
                        if presentation_affiliations["status"]:
                            presentation_affiliations = presentation_affiliations["data"]
                            if presentation_affiliations:
                                presentation_affiliations = presentation_affiliations
                                print(presentation_affiliations)
                            else:
                                logger.error("No presentation affiliations found.")


                        presentation_time_xpath = WEBSITE_CONFIG['asco'].get('presentationtime_xpath')
                        presentation_time_parts = extract_presentation_time(driver, presentation_time_xpath) if presentation_time_xpath else []
                        if presentation_time_parts["status"]:
                            presentation_time_parts = presentation_time_parts["data"]
                            if presentation_time_parts:
                                presentation_time_parts = presentation_time_parts
                            else:
                                logger.error("No presentation times found.")


                        presentation_link_xpath =WEBSITE_CONFIG['asco'].get('presentation_link')
                        presentation_link_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, presentation_link_xpath)))
                        
                        if isinstance(presentation_titles, list):
                           for i in range(len(presentation_titles)):
                                presentation_full_time = presentation_time_parts[i].get('p_time', '') if presentation_time_parts else ''
                                presentation_start_time = presentation_time_parts[i].get('p_start_time', '') if presentation_time_parts else ''
                                presentation_end_time = presentation_time_parts[i].get('p_end_time', '') if presentation_time_parts else ''
                                presentation_timezone = presentation_time_parts[i].get('p_time_zone', '') if presentation_time_parts else ''


                                if  presentation_link_elements and i < len(presentation_link_elements):
                                   presentation_link_element = presentation_link_elements[i]
                                   presentation_link_text_value = presentation_link_element.get_attribute('href')
                                   link_text = presentation_link_element.text.strip()
                                   presentation_link_text = f'=HYPERLINK("{presentation_link_text_value}", "{link_text}")'
                                else:
                                   presentation_link_text = ''

                                combined_data["Event Type"].append(session_event_type)
                                combined_data["Date"].append(session_date)
                                combined_data["Time"].append(presentation_full_time)
                                combined_data["Start Time"].append(presentation_start_time)
                                combined_data["End Time"].append(presentation_end_time)
                                combined_data["Time Zone"].append(presentation_timezone)
                                combined_data["Location"].append(";".join(session_location_text))
                                combined_data["Session Type"].append(session_type_elements)
                                combined_data["Session Details"].append(f"{session_type_elements};{session_location_text};{presentation_titles[i]}")
                                combined_data["Title"].append(presentation_titles[i])
                                combined_data["Abs"].append(presentation_link_text)
                                combined_data["Disease"].append(session_diseases)
                                combined_data["Authors"].append(presentation_authors[i] if presentation_authors else "")
                                combined_data["Affiliations"].append(presentation_affiliations[i] if presentation_affiliations else "")
                                combined_data["Details"].append("No Details Found")
                                combined_data["Source"].append(presentation_link_text_value)
                            
                        driver.execute_script("window.history.go(-1)")
                        time.sleep(WEBSITE_CONFIG['asco']['sleep_duration'])  # Sleep after navigating back
                        elements = find_elements(driver, WEBSITE_CONFIG['asco']['findelements'])
                           
                else:
                    logger.error(session_time_parts_result["message"])

            except StaleElementReferenceException as se:
                logger.warning(f"Stale Element Reference Exception: {se}")

            except TimeoutException as te:
                logger.error(f"Timeout exception occurred at index {index}: {te}")
    except Exception as e:
        logger.error(f"Error occurred during web scraping: {e}")

    finally:
        if driver:
            driver.quit()  # Quit WebDriver session
 
            # Convert combined_data to a DataFrame
            df = pd.DataFrame(combined_data)
            # Save DataFrame to Excel
            output_file = "AACO_567467.xlsx"
            df.to_excel(output_file, index=False)  # Save to Excel file
            logger.info(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    main()

# Module2/__init__.py
from .s2iHelperFunctions import getDomainName, getReturnArray, loadJSON, getPrompt, unpackDict2Str, checkPath

from .s2iWebKit import initialize_webdriver, scrape_url, find_elements, click_element_multiple_retries

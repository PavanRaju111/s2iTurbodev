# Define URLs and XPaths for scraping
WEBSITE_CONFIG = {
    'asco': {
        'sleep_duration': 5,  # Sleep duration in seconds between actions
        'url': 'https://meetings.asco.org/meetings/2024-asco-annual-meeting/316/program-guide/scheduled-sessions',  # URL to scrape
        'url1': 'https://www.abstractsonline.com/pp8/#!/20272/sessions/@sessiontype=Poster%20Session/1',  # URL to scrape
        'findelements': '//*[contains(concat( " ", @class, " " ), concat( " ", "session-card", " " ))]',  # XPath to find session cards
        'findelementss': "//ul[@id='results']//li",  # XPath to find session cards
        'title_element': '//h3[@_ngcontent-serverapp-c253]',  # XPath for session titles
        'session_authors_xpath': "//div[@class='col']/p[@data-cy='chairs']//h5[@class='m-0 p-0 text-14']",  # XPath for session authors
        'session_authors_affiliations_xpath': "//div[@class='col']/p[@data-cy='chairs']//p[@class='m-0 p-0 text-12 ng-star-inserted']",  # XPath for session authors' affiliations
        'dateandtime_element': '//*[@data-cy="time"]/span',  # XPath for date and time information
        'session_type': '//span[@_ngcontent-serverapp-c131]',  # XPath for session types
        'location': "//p[@data-cy='location']",  # XPath for session locations
        'event_type': "//p[@data-cy='meeting']/span/span",  # XPath for event types
        'session_details': '//h3[@_ngcontent-serverapp-c253]',  # XPath for session details
        'disease': "//p[@data-cy='tracks']",  # XPath for diseases
        'authors': "//h5[@class='m-0 p-0 text-14']",  # XPath for authors
        'affiliations': "//p[@class='m-0 p-0 text-12 ng-star-inserted']",  # XPath for author affiliations
        'presentation_title': ".//h6[@class='my-2']",  # XPath for presentation titles
        'presentation_affiliations': ".//p[@class='m-0 p-0 text-12 ng-star-inserted']",  # XPath for presentation affiliations
        'presentation_authors': ".//h5[@class='m-0 p-0 text-14']",  # XPath for presentation authors
        'presentation_section': "//div[contains(@id, 'presentation')]",  # XPath for presentation sections
        'presentationtime_xpath': "//div[@class='presentation-time small ng-star-inserted']",  # XPath for presentation times
        'presentation_link': "//div[contains(@id, 'presentation')]//a",  # XPath for presentation links
        'session_types': "//p[@data-cy='type']/span/span"  # XPath for session types
    }
}



### These are generic helper functions that are used across s2i Turbokit #####
import re, json, os

# Extract the domain name from any given URL and return the name as string
# getDomainName("https://www.example.com/path/to/page") will return 'example.com'
# getDomainName("http://sub.example.co.uk/some-page") will return sub.example.co.uk
def getDomainName(url):
    # Define a regular expression pattern for extracting the domain
    pattern = r"(https?://)?(www\d?\.)?(?P<domain>[\w\.-]+\.\w+)(/\S*)?"

    # Use re.match to search for the pattern at the beginning of the URL
    match = re.match(pattern, url)

    # Check if a match is found
    if match:
        # Extract the domain from the named group "domain"  
        domain = match.group("domain")
        return domain
    else:
        return 'None'

# Format a status, message, and data into a returnArray
def getReturnArray(status, message, data):
    if type(data) is not list:
        data = [data]
    returnArray = {
        "status": status,
        "message": message,
        "data": data
    }
    return returnArray

# Load json data from path
def loadJSON(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data

# Write to json
def writeJSON(data, out_path):
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        returnArray = getReturnArray(True, f'Data written to {out_path}', '')
    except Exception as e:
        returnArray = getReturnArray(False, e, '')
    return returnArray

# Formats an instruction string, query string, and context string into a final prompt
def getPrompt(instruction_prompt, query_prompt, context):
    p = f'{instruction_prompt}\n{query_prompt}'
    prompt = f'{p}\n{context}'
    return prompt

# Unpack dictionary as string
def unpackDict2Str(dict):
    array2str = []
    for key in dict:
        value = dict[key]
        stringKey = str(key)
        stringVal = str(value)
        fString = f'{stringKey}:{stringVal},'
        array2str.append(fString)
    finalString = '\n'.join(array2str)
    finalString = re.sub('^\\[', '', finalString)
    finalString = re.sub('\\]$', '', finalString)
    return finalString

# checks if path exists, if not creates path
def checkPath(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        returnArray = getReturnArray(True, '', directory)
    except Exception as e:
        returnArray = getReturnArray(False, e, '')
    return returnArray
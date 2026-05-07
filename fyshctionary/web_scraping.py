import requests
from bs4 import BeautifulSoup
import boto3
import time
import logging

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
DYNAMODB_TABLE_NAME = "UK_Fish_Dictionary"
AWS_REGION = "us-east-1"
BASE_URL = "https://www.anglingdirect.co.uk"

# --- UTILITY FUNCTIONS ---

def download_web_page_html(url: str) -> str:
    """
    Fetches raw HTML from the internet.
    Network communication and error handling only.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as error:
        logging.error(f"Could not download {url}: {error}")
        return None

def extract_individual_fish_links(main_page_html: str) -> list:
    """Parses the main species guide page to find links to individual fish profiles.
    Uses BeautifulSoup to navigate the HTML structure and extract relevant URLs and water type classifications.
    """
    soup = BeautifulSoup(main_page_html, 'html.parser')
    species_items = soup.find_all('li', class_='fish') 
    
    fish_tasks = []
    
    for item in species_items:
        # We delegate the messy work to our helpers
        url = _get_safe_fish_url(item)
        water_type = _classify_water_type(item.get('class', []))
        
        if url:
            fish_tasks.append({
                "url": url,
                "water_type": water_type
            })
            
    return fish_tasks

# --- HELPER ABSTRACTIONS (Private Logic) ---

def _get_safe_fish_url(item_soup) -> str:
    """
    Finds the correct link to the fish profile within the fish card.
    """
    # 1. Find all links within this fish card
    links = item_soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        
        # 2. VALIDATION LOGIC:
        if "/species-guide/" in href and "iucnredlist" not in href:
            if href.strip('/') != "https://www.anglingdirect.co.uk/species-guide":
                # Clean up relative links (/species-guide/carp -> https://...)
                return href if href.startswith('http') else f"{BASE_URL}{href}"
                
    return None

def _classify_water_type(classes: list) -> str:
    """
    Looks at the list of CSS classes on the <li> tag and matches them 
    to our internal categories.
    """
    # We use the Base64 strings found in the site's source code
    if "RnJlc2ggV2F0ZXI_" in classes:
        return "Freshwater"
    if "U2VhIFdhdGVy" in classes:
        return "Saltwater"
    
    return "All" # Fallback

def contains_label_text(text_node: str, target_label: str) -> bool:
    """
    Determines if a specific piece of text exists within an HTML element.
    Logic: 
    1. Check if the text node actually exists (isn't empty).
    2. Check if the target word (e.g., 'Habitat') is inside that text.
    """
    if text_node is None:
        return False
        
    return target_label in text_node

def extract_stat_by_label(soup_object: BeautifulSoup, label_text: str) -> str:
    """
    Finds a specific value in the 'Species Stats' sidebar.
    Targeted searching using a named helper function.
    """

    all_text_nodes = soup_object.find_all(string=True)
    
    target_node = None
    for node in all_text_nodes:
        if label_text in node:
            target_node = node
            break

    if target_node and target_node.parent:
        # Get the text from the container (e.g., <li>Habitat: Freshwater</li>)
        full_text = target_node.parent.get_text(strip=True)
        
        # Clean up the string to leave only the value
        clean_value = full_text.replace(label_text, "")
        return clean_value.strip(": ").strip()
    
    return "Not specified"

# --- CORE LOGIC FUNCTIONS ---

def parse_fish_species_data(html_content: str, source_url: str, water_type: str) -> dict:
    """
    Transforms raw HTML into a structured Python Dictionary.
    Mapping the website's layout to your database fields.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extracting the names
    common_name = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Unknown Fish"
    
    # In your provided URL, the Latin name is often in a specific paragraph class
    latin_name_element = soup.find('p', class_='technical')
    latin_name = latin_name_element.get_text(strip=True).replace("Aka ", "") if latin_name_element else "N/A"

    image_element = soup.find('div', class_='img').find('img') if soup.find('div', class_='img') else None
    image_url = image_element['src'] if image_element else "https://via.placeholder.com/200"

    # Creating the item dictionary for DynamoDB
    return {
        "fish_id": source_url.split('/')[-1],
        "common_name": common_name,
        "latin_name": latin_name,
        "image_url": image_url,
        "water_type": water_type,
        "status": extract_stat_by_label(soup, "Status"),
        "habitat": extract_stat_by_label(soup, "Habitat"),
        "bait": extract_stat_by_label(soup, "Bait"),
        "fishing_tackle": extract_stat_by_label(soup, "Fishing Tackle"),
        "native_or_invasive": extract_stat_by_label(soup, "Native or Invasive"),
        "where": extract_stat_by_label(soup, "Where"),
        "description": soup.find('div', class_='species-description').get_text(strip=True) if soup.find('div', class_='species-description') else "No description available.",
        "source_url": source_url,
        "last_updated": int(time.time())
    }

def upload_item_to_aws_dynamodb(data_dictionary: dict) -> None:
    """
    Sends the dictionary to the AWS cloud.
    AWS SDK (Boto3) interaction only.
    """
    resource = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = resource.Table(DYNAMODB_TABLE_NAME)
    try:
        table.put_item(Item=data_dictionary)
        logging.info(f"Database Updated: {data_dictionary['common_name']}")
    except Exception as error:
        logging.error(f"AWS Upload Error: {error}")

# --- THE EXECUTION MANAGER ---

def run_full_database_update() -> None:
    logging.info("--- Starting UK Fish Dictionary Sync ---")

    main_html = download_web_page_html(f"{BASE_URL}/species-guide")
    if not main_html:
        return

    # This now returns a list of dictionaries like: {'url': '...', 'water_type': 'Freshwater'}
    fish_tasks = extract_individual_fish_links(main_html)

    for task in fish_tasks:
        logging.info(f"Downloading and parsing: {task['url']}")
        individual_html = download_web_page_html(task['url'])
        if individual_html:
            # We pass the pre-identified water_type into the parser
            fish_data = parse_fish_species_data(individual_html, task['url'], task['water_type'])
            upload_item_to_aws_dynamodb(fish_data)
        
        time.sleep(2)

    logging.info("--- Sync Complete: DynamoDB is up to date ---")

if __name__ == "__main__":
    run_full_database_update()
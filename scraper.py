import os
import requests
import urllib3
from bs4 import BeautifulSoup

# Suppress annoying terminal warnings about old academic security certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_directory_index(directory_url="ignored"):
    """
    Parses straight line-by-line text copied from the UCR table.
    Uses the email address as the delimiter to group varying data lengths.
    """
    print("Executing Flat-Text Parser...")
    professors = []
    
    if not os.path.exists("bcoe_professors.txt"):
        print("ERROR: Could not find 'bcoe_professors.txt'.")
        print("Please make sure it is in the same folder as this script.")
        return []

    try:
        with open("bcoe_professors.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        headers = ["Name", "Department", "Phone", "Email", "Social Links"]
        clean_lines = [line for line in lines if line not in headers]

        buffer = []
        for line in clean_lines:
            buffer.append(line)
            
            if "@ucr.edu" in line:
                name = buffer[0]
                email = line
                
                middle_data = buffer[1:-1]
                title_and_dept = [item for item in middle_data if not item.startswith("(")]
                combined_title = " | ".join(title_and_dept)
                
                if not combined_title:
                    combined_title = "Engineering Faculty"

                slug = email.split('@')[0].strip()
                short_url = f"https://profiles.ucr.edu/{slug}"
                
                if not any(p['name'] == name for p in professors):
                    professors.append({
                        "name": name,
                        "title": combined_title,
                        "email": email,
                        "url": short_url
                    })
                
                buffer = []

        print(f"🔥 PARSE SUCCESS! Extracted {len(professors)} professors from raw text.")
        return professors
        
    except Exception as e:
        print(f"Parse Error: {e}")
        return []

def extract_personal_website(profile_url):
    """
    Visits an individual UCR profile page and extracts the personal/lab website link.
    """
    print(f"Scraping profile for lab website: {profile_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(profile_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Blocked by firewall (Status {response.status_code}).")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']
            if link.parent and 'Website' in link.parent.get_text():
                print(f"Target Acquired: {href}")
                return href

        print("No personal website found on this profile.")
        return None

    except Exception as e:
        print(f"Profile Scrape Error: {e}")
        return None

def scrape_professor_data(profile_url):
    """
    VACUUM MODE: Visits a professor's lab website and extracts all visible text, 
    designed to handle ancient academic HTML formatting and bypass basic firewalls.
    """
    print(f"Scraping detailed dossier from: {profile_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        # verify=False bypasses expired university SSL certs
        response = requests.get(profile_url, headers=headers, timeout=15, verify=False)

        if response.status_code != 200:
            print(f"Firewall blocked request (Status {response.status_code}).")
            return "Detailed research data could not be loaded due to university firewall."

        soup = BeautifulSoup(response.text, 'html.parser')

        # Rip out hidden code and navigation menus so the AI doesn't read them
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()

        # Grab every single piece of visible text
        text = soup.get_text(separator=' ', strip=True)
        
        import re
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit to 6000 characters to protect AI context window
        if len(cleaned_text) > 6000:
            cleaned_text = cleaned_text[:6000] + "... [Text truncated for AI processing]"
            
        print(f"✅ Success! Extracted {len(cleaned_text)} characters of raw research data.")
        return cleaned_text

    except Exception as e:
        print(f"Dossier Scrape Error: {e}")
        return "Detailed research data could not be loaded."
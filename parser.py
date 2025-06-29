
import json
import re
from html import unescape

def parse_plant_info(plant_html):
    """
    Parses the HTML for a single plant entry to extract its details.
    """
    try:
        # Extract link and primary name
        link_match = re.search(r'<a href="([^"]+)">([^<]+)</a>', plant_html)
        if not link_match:
            return None, f"Could not find link in {plant_html}"
        
        link = "https://www.aspca.org" + link_match.group(1)
        name = link_match.group(2)

        # The rest of the info is in the span after the link
        remaining_info = plant_html[link_match.end():]
        
        other_names = ""
        other_names_match = re.search(r'\(([^)]+)\)', remaining_info)
        if other_names_match:
            other_names = other_names_match.group(1).strip()

        scientific_name = ""
        scientific_name_match = re.search(r'<b>Scientific Names:</b>\s*<i>([^<]+)</i>', remaining_info)
        if scientific_name_match:
            scientific_name = scientific_name_match.group(1).strip()

        family = ""
        family_match = re.search(r'<b>Family:</b>\s*([^<]+)</span>', remaining_info)
        if family_match:
            family = family_match.group(1).strip()

        plant_data = {
            "name": name,
            "link": link
        }
        if other_names:
            plant_data["other_names"] = other_names
        if scientific_name:
            plant_data["scientific_name"] = scientific_name
        if family and family.strip():
            plant_data["family"] = family
            
        return plant_data, None

    except Exception as e:
        return None, str(e)

def main():
    """
    Main function to read the HTML file, parse the plant lists,
    and write the data to JSON files.
    """
    try:
        with open('website.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: website.html not found.")
        return

    # Unescape HTML entities
    html_content = unescape(html_content)

    toxic_plants = []
    safe_plants = []
    failed_plants = []

    # Regex to find the toxic and non-toxic sections
    toxic_section_match = re.search(r'h2>Plants Toxic to Cats</h2>.*?<div class="view-content">(.*?)<div class="attachment attachment-after">', html_content, re.DOTALL)
    nontoxic_section_match = re.search(r'h2>Plants Non-Toxic to Cats</h2>.*?<div class="view-content">(.*?)<footer', html_content, re.DOTALL)

    if toxic_section_match:
        toxic_html = toxic_section_match.group(1)
        plant_entries = re.findall(r'<div class="views-row.*?">(.*?)</div>', toxic_html, re.DOTALL)
        for entry in plant_entries:
            plant_info, error = parse_plant_info(entry)
            if plant_info:
                toxic_plants.append(plant_info)
            else:
                failed_plants.append({"html": entry.strip(), "error": error})

    if nontoxic_section_match:
        nontoxic_html = nontoxic_section_match.group(1)
        plant_entries = re.findall(r'<div class="views-row.*?">(.*?)</div>', nontoxic_html, re.DOTALL)
        for entry in plant_entries:
            plant_info, error = parse_plant_info(entry)
            if plant_info:
                safe_plants.append(plant_info)
            else:
                failed_plants.append({"html": entry.strip(), "error": error})

    # Write to JSON files
    with open('toxic.json', 'w', encoding='utf-8') as f:
        json.dump(toxic_plants, f, indent=4)

    with open('safe.json', 'w', encoding='utf-8') as f:
        json.dump(safe_plants, f, indent=4)

    with open('failed.json', 'w', encoding='utf-8') as f:
        json.dump(failed_plants, f, indent=4)

    print("Parsing complete. Files 'toxic.json', 'safe.json', and 'failed.json' have been created.")

if __name__ == "__main__":
    main()

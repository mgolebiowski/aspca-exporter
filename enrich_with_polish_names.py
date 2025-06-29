
import json
import os
import logging
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Set up logging
logging.basicConfig(filename='enrichment.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE_URL = os.getenv("DEEPSEEK_API_BASE_URL")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE_URL
)

CACHE_FILE = 'cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_to_cache(cache, type, scientific_name, polish_name):
    if type not in cache:
        cache[type] = {}
    cache[type][scientific_name] = polish_name
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4)

def get_polish_name(scientific_name, cache, type):
    if not scientific_name:
        return None, None

    if type in cache and scientific_name in cache[type]:
        logging.info(f"Using cached Polish name for: {scientific_name}")
        return scientific_name, cache[type][scientific_name]

    logging.info(f"Requesting Polish name for: {scientific_name}")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a script that translates scientific plant names to Polish. For each request, return a simple common polish name. No extra words. . Return either a common Polish name or empty string"},
                {"role": "user", "content": f'{scientific_name}'}
            ],
            max_tokens=60,
            temperature=0.1,
        )
        polish_name = response.choices[0].message.content.strip()
        logging.info(f"Received response for {scientific_name}: {polish_name}")
        if polish_name.lower() == 'not found':
            save_to_cache(cache, type, scientific_name, None)
            return scientific_name, None
        save_to_cache(cache, type, scientific_name, polish_name)
        return scientific_name, polish_name
    except Exception as e:
        logging.error(f"Error calling DeepSeek API for {scientific_name}: {e}")
        return scientific_name, None

def enrich_file(file_path, failed_enrichment_list, cache, type):
    with open(file_path, 'r', encoding='utf-8') as f:
        plants = json.load(f)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_plant = {executor.submit(get_polish_name, plant.get("scientific_name"), cache, type): plant for plant in plants}
        for future in tqdm(concurrent.futures.as_completed(future_to_plant), total=len(plants), desc=f"Enriching {os.path.basename(file_path)}"):
            plant = future_to_plant[future]
            try:
                scientific_name, polish_name = future.result()
                if polish_name:
                    plant["polish_name"] = polish_name
                else:
                    failed_enrichment_list.append(plant)
            except Exception as exc:
                logging.error(f'{plant.get("name")} generated an exception: {exc}')
                failed_enrichment_list.append(plant)


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(plants, f, indent=4)

def main():
    cache = load_cache()
    failed_enrichment = []
    enrich_file('toxic.json', failed_enrichment, cache, 'toxic')
    enrich_file('safe.json', failed_enrichment, cache, 'safe')

    with open('failed_enrichment.json', 'w', encoding='utf-8') as f:
        json.dump(failed_enrichment, f, indent=4)

    print("Enrichment complete. Files 'toxic.json', 'safe.json', and 'failed_enrichment.json' have been updated.")

if __name__ == "__main__":
    main()

# ASPCA Plant Data Extractor and Enricher

This project provides scripts to extract plant toxicity data from the ASPCA website, categorize it, and enrich the data with Polish common names using an AI model.

## Data Preparation

Before running the scripts, you need to download the ASPCA plant list webpage:

1.  Go to: `https://www.aspca.org/pet-care/animal-poison-control/cats-plant-list`
2.  Save the entire webpage as `website.html` in the root directory of this project.
    *   In most browsers, you can do this by right-clicking on the page and selecting "Save as..." or by going to `File > Save Page As...`.
3. Create .env file with DEEPSEEK_API_KEY and DEEPSEEK_API_BASE_URL values. You can also use any other model that exposes OpenAPI-like API.

## Setup and Usage

This project uses a `Makefile` to simplify the process. Make sure you have `make` installed on your system.

1.  **Install Dependencies**:
    ```bash
    make install
    ```
    This command will install all necessary Python packages listed in `requirements.txt`.

2.  **Parse Data**:
    ```bash
    make parse
    ```
    This command runs `parser.py`, which reads `website.html` and extracts plant information, categorizing them into `toxic.json` and `safe.json`. It also generates `failed.json` for any entries that could not be parsed.

3.  **Enrich Data with Polish Names**:
    ```bash
    make enrich
    ```
    This command runs `enrich_with_polish_names.py`, which uses an AI model (DeepSeek via OpenAI API) to fetch Polish common names for the plants in `toxic.json` and `safe.json`. The enriched data updates these files, and any plants that failed to enrich will be listed in `failed_enrichment.json`.

4.  **Run All Steps (Install, Parse, Enrich)**:
    ```bash
    make all
    ```
    This single command will execute all the above steps in sequence.

5.  **Clean Generated Files**:
    ```bash
    make clean
    ```
    This command removes all generated JSON data files (`cache.json`, `failed.json`, `failed_enrichment.json`, `toxic.json`, `safe.json`) and the `enrichment.log` file.

## Output Files

*   `toxic.json`: Contains a list of plants toxic to cats, with their scientific names and (after enrichment) Polish common names.
*   `safe.json`: Contains a list of plants non-toxic to cats, with their scientific names and (after enrichment) Polish common names.
*   `failed.json`: Contains HTML snippets of plant entries that the `parser.py` script failed to process.
*   `failed_enrichment.json`: Contains plant entries for which the `enrich_with_polish_names.py` script could not retrieve a Polish name.
*   `cache.json`: Stores cached Polish names to avoid repeated API calls.
*   `enrichment.log`: Logs information and errors from the enrichment process.

## Possible Improvements

*   **Pre-load Cache**: Implement a mechanism to pre-load `cache.json` before making any DeepSeek API calls to further reduce redundant requests.
*   **Prompt Engineering**: Experiment with different prompts for the AI model to improve translation accuracy and consider adding a confidence level to the results. Explore iterative prompting for more challenging names.
*   **Post-processing**: Add a step to clean up the enriched list, such as standardizing capitalization of Polish names.

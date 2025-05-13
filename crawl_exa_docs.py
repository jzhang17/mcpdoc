import os
import sys
from exa_py import Exa
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file in the current directory
    # This assumes the script is run from the 'mcpdoc' directory or the .env is there
    # If running from workspace root, it might look for .env there. Let's adjust path.
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Look for .env next to the script
    load_dotenv(dotenv_path=dotenv_path) # Load the .env file
    
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        print(f"Error: EXA_API_KEY environment variable not set or found in {dotenv_path}.", file=sys.stderr)
        sys.exit(1)

    exa = Exa(api_key)
    output_dir = "mcpdoc/llm-txt-extraction"
    output_file = os.path.join(output_dir, "exa_docs.llm.txt")
    target_url = "https://docs.exa.ai/"
    # Keywords to target within subpages, based on Exa's sitemap/structure
    subpage_targets = [
        "docs", "reference", "concepts", "examples", "integrations", "sdks", 
        "quickstart", "getting started", "api reference", "rag", "python sdk",
        "contents", "search", "findsimilar", "answer", "changelog", "faq",
        "crawling subpages", "livecrawl", "websets"
    ]

    print(f"Starting crawl of {target_url}...")
    try:
        results = exa.get_contents(
            [target_url],
            subpages=30,  # Increased subpage limit slightly for better coverage
            subpage_target=subpage_targets
        )

        all_text = ""
        if results and results.results:
            for result in results.results:
                # Defensive check for result type
                if not hasattr(result, 'url') or not hasattr(result, 'text'):
                    print(f"Skipping unexpected result format: {type(result)} - {result}")
                    continue 
                print(f"Processing main page: {result.url}")
                if result.text:
                    all_text += f"--- URL: {result.url} ---\n"
                    all_text += result.text.strip() + "\n\n"
                
                if hasattr(result, 'subpages') and result.subpages:
                    print(f"Found {len(result.subpages)} subpages for {result.url}")
                    for subpage in result.subpages:
                        # Defensive check for subpage type
                        if not hasattr(subpage, 'url') or not hasattr(subpage, 'text'):
                             print(f"Skipping unexpected subpage format: {type(subpage)} - {subpage}")
                             continue
                        print(f"  Processing subpage: {subpage.url}")
                        if subpage.text:
                           all_text += f"--- URL: {subpage.url} ---\n"
                           all_text += subpage.text.strip() + "\n\n"
        else:
            print("No results or subpages found.")

        if all_text:
            print(f"Writing extracted text to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(all_text)
            print("Successfully wrote content to file.")
        else:
            print("No text content extracted.")

    except Exception as e:
        print(f"An error occurred during crawling or processing: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 
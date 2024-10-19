import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import re
from urllib.parse import urlparse
import datetime

# Constants
GOOGLE_CSE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_SEARCHENGINE_ID = os.environ.get("GOOGLE_CSE_SEARCHENGINE_ID")
GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_table_of_contents(topic):
    prompt = f"""How should I structure an overview article titled '{topic}'.
    This should look like an article from McKinsey, BCG or the Financial Times.
    Outline a Table of Content. 
    For each main section, return a query to ask a search engine like Google to get the most relevant content, and then the prompt to use in order to craft the paragraph based on scrapped content from the web pages' content.
    The search queries should help gather the best content for the section, within the frame of the title.
    For the prompt, use the same language as the title '{topic}'.
    Return this as a JSON file, following this example:
    
    {{
      "tableOfContents": [
        {{
          "section": "Introduction: The Evolving Landscape of Banking Fraud",
          "query": "Banking fraud trends 2024, 2025",
          "prompt": "Write two paragraphs about 'Introduction: The Evolving Landscape of Banking Fraud' based on the following aggregation of articles:"
        }},
        {{
          "section": "AI's Role in Antifraud: From Detection to Prevention",
          "query": "AI applications in banking fraud prevention",
          "prompt": "Write two paragraphs about 'AI's Role in Antifraud: From Detection to Prevention' based on the following aggregation of articles:"
        }},
        etc.
      ]
    }}
    """
    response = model.generate_content(prompt)
    print("Raw response:")
    print(response.text)
    
    # Try to extract JSON content using regex
    json_match = re.search(r'\{[\s\S]*\}', response.text)
    if json_match:
        json_content = json_match.group(0)
    else:
        raise ValueError("No JSON content found in the response")
    
    
    try:
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # If JSON parsing fails, return a minimal valid structure
        return {"tableOfContents": []}

def google_search(query, api_key, cse_id, **kwargs):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
    }
    params.update(kwargs)
    response = requests.get(url, params=params)
    return response.json()

def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:20000]  # Limit to first 20000 characters
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""

def generate_section_content(prompt, scraped_content):
    full_prompt = f"""{prompt}. 
    Format everything as HTML code. 
    Create sub-sections if required. 
    Add a reference section at the end of the paragraph with the source URLs. 
    Format the reference section as a list of URLs, each with a number - the same number is referenced in the text where the URL is used.
    Use only content from the provided sources.
    \n\n{scraped_content}
"""
    
    try:
        response = model.generate_content(full_prompt)
        content = response.text
        
        # Remove code block markers
        content = re.sub(r'```html\n?', '', content)
        content = re.sub(r'```\n?', '', content)
        
        # Remove outer <html> and <body> tags if present
        content = re.sub(r'^\s*<html>\s*<body>\s*', '', content)
        content = re.sub(r'\s*</body>\s*</html>\s*$', '', content)
        
        return content.strip()
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return f"<p>Error generating content for this section.</p>"

def reformulate_article(content):
    prompt = """Please enhance the following article's clarity, coherence, and style while maintaining its structure and information. 
    Make sure that it is a well-structured article, with a clear introduction, body and conclusion.
    Make sure that it addresses the topic and the questions it raises.
    Ensure the output is in valid HTML, preserving all tags and structure. 
    After the main title, include a table of contents with links to each section.
    At the end, add a references section with URLs cited in the text. 
    Ensure reference numbers match the new order, are clickable, and navigate to the correct URL in the references section. 
    Avoid duplicating URLs in the references.

    Here's the article:

    """
    
    full_prompt = prompt + content
    
    try:
        response = model.generate_content(full_prompt)
        reformulated_content = response.text
        
        # Remove any outer HTML and body tags if present
        reformulated_content = re.sub(r'^\s*<html>\s*<body>\s*', '', reformulated_content)
        reformulated_content = re.sub(r'\s*</body>\s*</html>\s*$', '', reformulated_content)
        
        return reformulated_content.strip()
    except Exception as e:
        print(f"Error reformulating content: {str(e)}")
        return content  # Return original content if reformulation fails


def main():
    topic = input("Enter the topic for the article: ")
    toc = get_table_of_contents(topic)

    full_content = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{topic}</title>\n</head>\n<body>\n"
    full_content += f"<h1>{topic}</h1>\n"

    for section in toc['tableOfContents']:
        print(f"Processing section: {section['section']}")
        search_results = google_search(section['query'], GOOGLE_CSE_API_KEY, GOOGLE_CSE_SEARCHENGINE_ID, num=5)
        
        scraped_content = ""
        for item in search_results.get('items', []):
            url = item['link']
            content = scrape_content(url)
            scraped_content += f"\n\nSource: {url}\n{content}"
        
        section_content = generate_section_content(section['prompt'], scraped_content)
        
        full_content += f"<h2>{section['section']}</h2>\n"
        full_content += f"{section_content}\n"

    full_content += "</body>\n</html>"

    print("Initial article generated. Now reformulating...")
    reformulated_content = reformulate_article(full_content)

    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_article_{timestamp}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(reformulated_content)

    print(f"Reformulated article generated and saved as '{filename}'")

if __name__ == "__main__":
    main()

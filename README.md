# AI Report Writer

This project is an AI-powered content generator that creates structured articles based on user-provided topics. It uses Google Custom Search for web scraping and Google's Gemini AI for content generation.

## Features

- Generates a table of contents for a given topic
- Performs web searches and scrapes relevant content
- Uses AI to generate section content based on scraped information
- Produces a final HTML article

## Prerequisites

- Python 3.7 or higher
- Google Custom Search Engine API key
- Google Custom Search Engine ID
- Google Gemini API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/omathurin/ai-report-writer.git
   cd ai-report-writer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root directory.
2. Add your API keys to the `.env` file:
   ```
   GOOGLE_CSE_API_KEY=your_google_cse_api_key
   GOOGLE_CSE_SEARCHENGINE_ID=your_google_cse_searchengine_id
   GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
   ```
   Replace the placeholders with your actual API keys.

## Usage

Run the script:

```
python ai-report-writer.py
```


When prompted, enter the topic for your article. The script will then generate the content and save it as an HTML file named `generated_article.html` in the same directory.

## Project Structure

- `ai-report-writer.py`: Main script for content generation
- `requirements.txt`: List of Python dependencies
- `.env`: Configuration file for API keys (not tracked by Git)
- `generated_article.html`: Output file (generated when the script is run)

## Customization

You can modify the `ai-report-writer.py` script to adjust:
- The number of search results used
- The prompt templates for AI content generation
- The HTML structure of the output file

## Troubleshooting

If you encounter any issues:
1. Ensure all dependencies are correctly installed
2. Verify that your API keys are correct and have the necessary permissions
3. Check your internet connection, as the script requires online access

## Note

This script makes API calls to Google services. Be aware of any usage limits or costs associated with the Google Custom Search API and Gemini AI.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

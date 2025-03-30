# PsychNews Connect

A Streamlit-powered educational tool that bridges AP Psychology terminology with current news events, using AI to generate contextual learning summaries for students.

## Overview

PsychNews Connect helps psychology students prepare for tests like the AP Psychology exam by connecting psychological concepts to current news events. The app:

1. Scans RSS feeds from high-quality news sources
2. Analyzes articles using OpenAI's API to identify psychological concepts
3. Creates educational summaries that explain how the news relates to specific psychology terms

## Features

- **Automated News Scanning**: Daily scheduled scans of news sources for psychology-related content
- **AI-Powered Analysis**: Identification of underlying psychological principles even when terms aren't explicitly mentioned
- **Educational Summaries**: AI-generated explanations of the relationship between news events and psychology terms
- **Reference Library**: Access to 500+ psychology terms and definitions
- **Filtering Options**: Ability to filter news by specific psychology concepts

## Technical Details

- **Framework**: Streamlit
- **APIs**: OpenAI (GPT-4)
- **Data Sources**: RSS feeds from high-quality psychology and news websites
- **Data Storage**: Local JSON/CSV files

## Setup & Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key as an environment variable
4. Run the application:
   ```
   streamlit run app.py
   ```

## Requirements

- Python 3.7+
- OpenAI API key
- Required Python packages (see requirements.txt)

## License

[MIT License](LICENSE)
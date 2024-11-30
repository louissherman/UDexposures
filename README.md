# Underdog Draft Exposures Dashboard

A Streamlit dashboard for analyzing your Underdog Fantasy draft exposures for both NFL and NBA contests. (plans to add additional sports in the future)

## 🌟 Features

- **Multi-Sport Support**: Automatically detects and handles both NFL and NBA drafts
- **Detailed Exposure Analysis**: View your total exposure percentages across all drafts
- **Advanced Filtering**:
  - Search for specific players
  - Filter by position, team, draft pool, and individual drafts
  - See correlations between drafted players
- **Visual Analytics**:
  - Position distribution charts
  - Stack analysis
  - Draft timing patterns
- **Draft Metrics**:
  - Total number of drafts
  - Average draft position
  - Entry fee tracking

## 📊 Usage

1. Visit the [dashboard](https://underdog-exposures.streamlit.app/)
2. Upload your Underdog draft CSV file
3. Use the filters to analyze your draft portfolio
4. Search for specific players to see correlation data

## 📋 Required CSV Format

Your CSV file should include the following columns:
- First Name
- Last Name
- Position
- Team
- Draft Pool
- Draft Pool Title
- Draft Pool Entry Fee
- Draft Entry
- Pick Number
- Picked At

## 🚀 Local Development

1. Clone the repository 
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run exposures.py`

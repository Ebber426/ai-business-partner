
# AI Business Partner – Digital Product Edition (MVP)

An intelligent agent system that acts as a digital product business partner. It researches trends, creates digital products (Google Sheets planners), logs all activity, and reports status via a Telegram Bot.

## Features

### V1 - Core Features
- **Research Agent**: Scrapes/queries trends (using `pytrends` or simulation) to find profitable keywords.
- **Creation Agent**: Generates Google Sheets templates (Daily Planners, Budget Trackers) based on research.
- **System Memory**: Logs all research, products, and activity to a central Google Sheet.

### V2 - Publishing Features
- **Publishing Agent**: Auto-publish products to Etsy and Pinterest.
- **OAuth Integration**: Secure authentication with marketplace APIs.

### Telegram Commands
| Command | Description |
|---------|-------------|
| `/start` | View all available commands |
| `/status` | Check system status |
| `/revenue` | View total revenue |
| `/whatdidyoudotoday` | View daily activity log |
| `/run` | Research + Create a product |
| `/publish` | Publish product to Etsy/Pinterest |
| `/auth_etsy` | Get Etsy authorization URL |
| `/auth_pinterest` | Get Pinterest authorization URL |

---

## Setup Instructions

### 1. Google Cloud Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **Google Sheets API** and **Google Drive API**.
4. Create a **Service Account**.
5. Create a JSON key for the service account and download it. Rename it to `credentials.json` and place it in the `ai-business-partner` folder.
6. **Important**: Copy the `client_email` from the JSON file.

### 2. Google Sheet Setup
1. Create a new Google Sheet.
2. Share it with the `client_email` (Editor access).
3. Copy the **Sheet ID** from the URL (e.g., `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`).
4. (Optional) The system will try to create tabs, but you can create them manually: `Research`, `Products`, `Activity Log`, `Revenue`.

### 3. Telegram Bot Setup
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow instructions.
3. Copy the **HTTP API Token**.

### 4. Project Configuration
1. Navigate to the `ai-business-partner` folder.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env`:
   - Fill in `TELEGRAM_BOT_TOKEN` and `GOOGLE_SHEET_ID`.
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your JSON file.

### 5. V2: Etsy & Pinterest Setup (Optional)

#### Etsy
1. Register at [developers.etsy.com](https://developers.etsy.com).
2. Create an app and get your **API Key** and **Secret**.
3. Get your **Shop ID** from your Etsy shop URL.
4. Fill in `.env`: `ETSY_API_KEY`, `ETSY_API_SECRET`, `ETSY_SHOP_ID`.
5. Run the bot, use `/auth_etsy`, and complete OAuth flow.

#### Pinterest
1. Register at [developers.pinterest.com](https://developers.pinterest.com).
2. Create an app and get your **App ID** and **Secret**.
3. Get your **Board ID** from your Pinterest board URL.
4. Fill in `.env`: `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_BOARD_ID`.
5. Run the bot, use `/auth_pinterest`, and complete OAuth flow.

---

## How to Run

1. Activate your virtual environment.
2. Run the orchestrator:
   ```bash
   python orchestrator.py
   ```
3. Open your Telegram Bot and send `/start`.
4. Send `/run` to trigger the AI agent cycle immediately.
5. Send `/publish` to publish the latest product to marketplaces.

## Directory Structure
```
ai-business-partner/
├── app/
│   ├── agents/
│   │   ├── research_agent.py    # Trend research
│   │   ├── creation_agent.py    # Google Sheets product creation
│   │   └── publishing_agent.py  # Etsy/Pinterest publishing
│   └── utils/
│       ├── google_sheets.py     # System memory
│       ├── telegram_bot.py      # Command center
│       ├── etsy_api.py          # Etsy OAuth + API
│       └── pinterest_api.py     # Pinterest OAuth + API
├── orchestrator.py              # Main entry point
├── config.py                    # Environment config
├── requirements.txt
└── .env                         # API keys (not committed)
```


# AI Business Partner – Digital Product Edition (MVP)

An intelligent agent system that acts as a digital product business partner. It researches trends, creates digital products (Google Sheets planners), logs all activity, and automates Pinterest marketing.

## Features

### V1 - Core Features
- **Research Agent**: Analyzes trends to find profitable digital product keywords.
- **Creation Agent**: Generates Google Sheets templates (Daily Planners, Budget Trackers) based on research.
- **System Memory**: Logs all research, products, and activity to a central database.

### V2 - Marketing Automation
- **Pinterest Agent**: Automatically creates pins to promote your products on Pinterest.
- **Manual Upload Workflow**: You manually upload products to your shop (e.g., Etsy, Gumroad). The app downloads the created file and automates Pinterest marketing.

### Web Interface Commands
| Feature | Description |
|---------|-------------|
| **Dashboard** | View system status & activity |
| **Research** | Browse and manage trend research |
| **Products** | Create new digital products from trends |
| **Publishing** | Publish to Pinterest for marketing |
| **Settings** | Configure API credentials |

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

### 3. Project Configuration
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
   - Fill in `GOOGLE_SHEET_ID`.
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your JSON file.

### 4. Pinterest Setup (Optional)
1. Register at [developers.pinterest.com](https://developers.pinterest.com).
2. Create an app and get your **App ID** and **Secret**.
3. Get your **Board ID** from your Pinterest board URL.
4. Fill in `.env`: `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_BOARD_ID`.
5. Run the app and complete Pinterest OAuth flow.

---

## How to Run

### Backend
1. Activate your virtual environment.
2. Run the FastAPI server:
   ```bash
   python -m uvicorn main:app --port 8000
   ```
   
### Frontend
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies (first time only):
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:5173`

### Workflow
1. **Research**: Click "Run Research" to find trending keywords.
2. **Create**: Select a trend and click "Create Product" to generate a Google Sheet template.
3. **Upload**: Manually upload the product to your shop (Etsy, Gumroad, etc.).
4. **Market**: Click "Publish to Pinterest" to automatically create marketing pins.

## Directory Structure
```
ai-business-partner/
├── app/
│   ├── agents/
│   │   ├── research_agent.py    # Trend research
│   │   ├── creation_agent.py    # Google Sheets product creation
│   │   └── publishing_agent.py  # Pinterest marketing automation
│   └── utils/
│       ├── google_sheets.py     # System memory
│       ├── local_db.py          # Local database
│       └── pinterest_api.py     # Pinterest OAuth + API
├── frontend/                    # React + Vite web interface
├── main.py                      # FastAPI backend
├── config.py                    # Environment config
├── requirements.txt
└── .env                         # API keys (not committed)
```

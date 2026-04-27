# RU Hack - AI Career Optimization Tool

RU Hack is a Python-based project that helps users analyze resumes, extract structured profile data, and generate personalized job recommendations through an interactive Streamlit interface.  
It combines local resume processing with webhook-based backend integration and optional cloud storage (Google Drive + Firebase).

## What This Project Does

- Upload and parse resumes (`PDF`, `DOCX`, `TXT`)
- Extract and clean resume text for downstream analysis
- Collect user preferences (locations, roles, job types, skills)
- Send profile data to an n8n webhook for backend processing
- Fall back to local analysis if backend calls fail
- Generate and display tailored job recommendations
- Export processed user profile data to `user_data_export.json`

## Repository Structure

```text
RU_HACK/
├── Frontend/                    # Streamlit application and UI modules
│   ├── main.py                  # Frontend launcher (direct or poetry mode)
│   ├── streamlit_app.py         # Main app entrypoint
│   ├── ARCHITECTURE.md          # Frontend module documentation
│   └── utils/
│       ├── validation.py
│       ├── resume_processor.py
│       ├── data_models.py
│       ├── backend_integration.py
│       └── n8n_webhook_client.py
├── Resume_Parser/               # Resume parsing and cloud upload helpers
│   ├── resume_parser.py
│   ├── firebase_config.py
│   └── gdrive_config.py
├── CLOUD_SETUP.md               # Cloud integration setup guide
├── watch_webhook.py             # Real-time watcher for exported webhook data
├── get_webhook_response.py      # CLI helper for viewing exported response data
├── pyproject.toml
└── requirements.txt
```

## Tech Stack

- Python 3.12+
- Streamlit
- PyMuPDF / pypdf / python-docx
- requests
- Firebase Admin SDK
- Google API Client libraries
- Poetry (recommended for dependency management)

## Quick Start

### 1) Install Dependencies

Using Poetry (recommended):

```bash
poetry install
```

Using pip:

```bash
pip install -r requirements.txt
```

### 2) Run the Frontend

From repository root:

```bash
python Frontend/main.py
```

Other run options:

```bash
# Run with Poetry flow
python Frontend/main.py poetry

# Direct Streamlit command
python -m streamlit run Frontend/streamlit_app.py
```

The app opens at `http://localhost:8501`.

## Application Flow

1. User uploads a resume or pastes resume text.
2. Resume text is extracted and editable in the UI.
3. User fills profile and job preference fields.
4. App sends payload to the n8n webhook endpoint.
5. If webhook/backend is unavailable, local fallback analysis runs.
6. Job recommendations are generated and shown in-app.
7. User data is exported to `user_data_export.json` for inspection/debugging.

## Cloud Integration (Optional)

Cloud upload is available for:
- Google Drive (resume file upload)
- Firebase Firestore (parsed profile and metadata)

See `CLOUD_SETUP.md` for full setup details, including credentials and API enablement steps.

## Useful Development Commands

### Code Formatting

```bash
# Format the whole project
poetry run black .

# Format one file
poetry run black Frontend/streamlit_app.py
```

### Run Tests (if/when test files are present)

```bash
poetry run pytest
```

## Webhook and Debug Utilities

- `watch_webhook.py`  
  Watches `user_data_export.json` in real time and prints updates.

- `get_webhook_response.py`  
  Shows current exported data and example webhook response structure.

- `show_webhook_response.py` / `terminal_webhook_viewer.py`  
  Additional local scripts for inspecting webhook-related output.

## Notes for Contributors

- Keep secrets and credential files out of version control.
- Use `.gitignore` for service account/OAuth JSON files.
- Prefer modular updates inside `Frontend/utils/` to keep `streamlit_app.py` focused on orchestration.

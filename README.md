# LegalEase AI

LegalEase AI is an AI-assisted legal documentation platform designed to help users generate structured first drafts of legal documents, review and edit those drafts, identify missing information, and export documents as professionally formatted PDFs.

> **Disclaimer:** LegalEase AI generates AI-assisted document drafts for educational and productivity purposes. It does not provide legal advice. Generated documents should be reviewed by a qualified legal professional before being signed, submitted, or relied upon.

## Overview

The application combines a web-based frontend with a Flask backend and the Groq API to provide an end-to-end document generation workflow.

The current system supports:

- AI-assisted legal document generation
- Dynamic document forms
- Structured document generation
- Missing-information detection
- Document warnings
- Editable generated drafts
- PDF generation and export
- Local document history
- Legal-context integration
- REST API endpoints
- Structured PDF formatting using ReportLab

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask
- Flask-CORS

### AI

- Groq API
- Configurable Groq models
- JSON Object Mode for structured responses

### PDF Generation

- ReportLab

### Storage

- Browser `localStorage` for document history
- Local filesystem for generated PDFs during development

## Project Structure

```text
AI-Legal-Documentation-Assistant/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── generated_docs/
│   │
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py
│       ├── legal_service.py
│       └── pdf_service.py
│
├── frontend/
│   └── index.html
│
├── legal_data/
│
├── .gitignore
└── README.md
```

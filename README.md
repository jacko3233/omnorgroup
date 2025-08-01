# HireSoft Job Manager

This repository contains a small Flask application for managing equipment hire jobs. It is intended as a white‑label solution – the displayed brand name and secret key can be configured through environment variables.

## Requirements

- Python 3.10 or newer
- The Python packages in `job_manager/requirements.txt`

## Setup

1. **Install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r job_manager/requirements.txt
   ```
2. **Set environment variables**
   - `APP_BRAND` – optional brand name shown in the UI (default: `HireSoft`)
   - `APP_SECRET_KEY` – secret key for session security (provide your own value in production)

3. **Run the app**
   ```bash
   python job_manager/app.py
   ```
   The server starts on http://localhost:8080/ and automatically creates `data.db` for storage.

## Deployment notes

For production deployments consider running the app with a WSGI server such as Gunicorn or hosting it in a Docker container. The bundled `omnorgroup-theme.zip` can be deployed separately if you also need the WordPress theme.

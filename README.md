# QA Engineer Portfolio

A retro sci-fi portfolio site for Julio Angulo built with Python, Flask, SQLite, HTML, CSS, and JavaScript.

## Features
- Home page with animated introduction text
- About page with professional interests and experience
- Projects page with GitHub project cards
- Contact page with submission form and recruiter contact details
- SQLite-backed contact storage

## Run locally
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the site:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.

## API
- `GET /ping`
  - Public health check
  - Response: `{"status": "ok", "message": "Portfolio API is available."}`
- `POST /login`
  - Request JSON: `{"username": "admin", "password": "password"}`
  - Response JSON: `{"access_token": "...", "refresh_token": "...", "token_type": "Bearer", "expires_in": 3600}`
- `POST /refresh`
  - Request JSON: `{"refresh_token": "..."}`
  - Response JSON: new `access_token` and `refresh_token`
- `GET /contacts`
  - Authenticated
  - Use header: `Authorization: Bearer <access_token>`
- `POST /contacts`
  - Authenticated
  - Request JSON fields: `full_name`, `email`, `phone`, `company`, `subject`, `message`
  - Returns the created contact record
- `GET /contacts/<id>`
  - Authenticated
  - Returns a contact by id
- `PUT /contacts/<id>`
  - Authenticated
  - Accepts partial or full contact fields in JSON
  - Updates the record
- `DELETE /contacts/<id>`
  - Authenticated
  - Deletes the record

## Notes
- The SQLite database is created automatically in `instance/portfolio.db`.
- Replace the placeholder contact info with your real email and phone number.
- Feel free to update the GitHub project links and descriptions in `app.py`.

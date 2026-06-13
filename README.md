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

## Notes
- The SQLite database is created automatically in `instance/portfolio.db`.
- Replace the placeholder contact info with your real email and phone number.
- Feel free to update the GitHub project links and descriptions in `app.py`.

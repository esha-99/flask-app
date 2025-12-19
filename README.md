# Secured Flask App (Lab Project)

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set a strong secret key (required)
export FLASK_SECRET_KEY="$(python -c "import secrets; print(secrets.token_urlsafe(32))")"

python app.py
```

Open: http://127.0.0.1:5000

## Security Controls Implemented
- Parameterized SQL queries for search
- Output encoding (escape) for user-controlled fields
- CSRF protection (Flask-WTF)
- Password hashing (Werkzeug)
- Basic rate limiting on login
- Security headers (CSP, HSTS, etc.)
- Disabled debug/info leakage endpoint

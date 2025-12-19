"""
✅ SECURED WEB APPLICATION
This is a hardened version of the original intentionally-vulnerable Flask app.

Changes include:
- Parameterized SQL queries (prevents SQL Injection)
- Output encoding (prevents reflected/stored XSS)
- Password hashing + safe auth checks
- Basic rate limiting for login
- CSRF protection for POST forms
- Safer session cookie settings
- Security headers (CSP, X-Frame-Options, etc.)
- Debug/info-leak endpoints removed / restricted
"""

from __future__ import annotations

import os
import sqlite3
import time
import secrets
from typing import Dict, Tuple, List

from flask import Flask, request, session, redirect, url_for, abort, render_template
from markupsafe import escape

# **SECURITY FIX:** CSRF protection for POST requests/forms
from flask_wtf.csrf import CSRFProtect  # type: ignore

# **SECURITY FIX:** Password hashing instead of plaintext passwords
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# **SECURITY FIX:** Load secret key from environment instead of hard-coding in source code
# Set it in your shell: export FLASK_SECRET_KEY="a-long-random-secret"
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_urlsafe(32)

# **SECURITY FIX:** Harden session cookies (best effort; SESSION_COOKIE_SECURE requires HTTPS)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,  # set to False only for local HTTP testing
)

csrf = CSRFProtect(app)

# -------------------------------------------------------------------
# Simple demo users (hashed). In production: store hashes in a DB + use MFA.
# -------------------------------------------------------------------
# **SECURITY FIX:** Store only password hashes (never plaintext)
_users_hashed = {
    "admin": generate_password_hash("admin123"),
    "user1": generate_password_hash("password123"),
    "test": generate_password_hash("test"),
}

# -------------------------------------------------------------------
# Very small in-memory rate limiter (demo)
# -------------------------------------------------------------------
# **SECURITY FIX:** Basic rate limiting to slow down brute-force attempts
LOGIN_LIMIT = 5           # max attempts
LOGIN_WINDOW_SEC = 60     # per window
_login_attempts: Dict[str, List[float]] = {}

def _client_ip() -> str:
    # NOTE: In production behind proxies, use ProxyFix + trusted proxy config.
    return request.remote_addr or "unknown"

def _rate_limit_ok(key: str) -> bool:
    now = time.time()
    window_start = now - LOGIN_WINDOW_SEC
    attempts = _login_attempts.get(key, [])
    attempts = [t for t in attempts if t >= window_start]
    _login_attempts[key] = attempts
    return len(attempts) < LOGIN_LIMIT

def _record_attempt(key: str) -> None:
    _login_attempts.setdefault(key, []).append(time.time())


def page(title: str, body_html: str):
    # body_html is authored server-side; any user-controlled values must be escaped before insertion.
    return render_template("base.html", title=title, body=body_html)

# -------------------------------------------------------------------
# Security headers
# -------------------------------------------------------------------
@app.after_request
def set_security_headers(resp):
    # **SECURITY FIX:** Add common security headers
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    # CSP: allow self only. (Inline styles exist in this demo, so allow 'unsafe-inline'.)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline';"
    # HSTS (only meaningful on HTTPS)
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp


@app.route("/")
def home():
    user = session.get("user")
    # Rendered via template
    return render_template("home.html", title="Home - Secured App", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    ip = _client_ip()

    if request.method == "POST":
        # **SECURITY FIX:** CSRF token is automatically validated by CSRFProtect on POST.
        if not _rate_limit_ok(ip):
            body = "<div class='error'>Too many attempts. Please try again later.</div>"
            return page("Login - Rate Limited", body), 429

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # **SECURITY FIX:** Constant-time hash verification using Werkzeug
        stored_hash = _users_hashed.get(username)
        _record_attempt(ip)

        if stored_hash and check_password_hash(stored_hash, password):
            session.clear()
            session["user"] = username
            return redirect(url_for("home"))
        # invalid credentials fall through to show the form with an error
        return render_template("login.html", title="Login", error=True)

    # GET
    return render_template("login.html", title="Login", error=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/search")
def search():
    query = request.args.get("q", "")

    # Demo: in-memory DB
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER, name TEXT, price REAL)")
    cursor.execute("DELETE FROM products")
    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?)",
        [(1, "Laptop", 999.99), (2, "Phone", 699.99), (3, "Tablet", 499.99), (4, "Headphones", 199.99)],
    )
    conn.commit()

    results: List[Tuple[int, str, float]] = []
    if query:
        try:
            # **SECURITY FIX:** Parameterized query (prevents SQL injection)
            cursor.execute("SELECT id, name, price FROM products WHERE name LIKE ?", (f"%{query}%",))
            results = cursor.fetchall()
        except Exception:
            results = []
    conn.close()

    # Render search template with results (Jinja handles escaping)
    return render_template("search.html", title="Search - Secured", q=query, results=results)


# Stored comments (escaped)
_comments: List[Tuple[str, str]] = []

@app.route("/comment", methods=["GET", "POST"])
def comment():
    user = session.get("user") or "anonymous"

    if request.method == "POST":
        # **SECURITY FIX:** CSRF token validated automatically (CSRFProtect)
        text = request.form.get("comment", "")

        # **SECURITY FIX:** Output encoding (prevents stored XSS)
        _comments.append((str(escape(user)), str(escape(text))))
        return redirect(url_for("comment"))
    items = "".join(f"<li><b>{u}</b>: {c}</li>" for u, c in _comments) or "<li>No comments yet.</li>"

    return render_template("comments.html", title="Comments", comments=_comments)


@app.route("/echo")
def echo():
    txt = request.args.get("text", "")
    # **SECURITY FIX:** Escape output to prevent reflected XSS
    return render_template("echo.html", title="Echo - Secured", txt=txt)


# **SECURITY FIX:** Remove/disable debug information leakage endpoint.
# If you need diagnostics, log safely and protect with admin auth + non-production config.
@app.route("/debug")
def debug_disabled():
    abort(404)


if __name__ == "__main__":
    # **SECURITY FIX:** Never run with debug=True in a deployed environment
    app.run(host="127.0.0.1", port=5000, debug=False)

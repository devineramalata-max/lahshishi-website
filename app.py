"""
Marketing Agency Website - Sell Your Car / Graphic Design / Entrepreneurial Course
-----------------------------------------------------------------------------------
HOW TO RUN IN PYCHARM:
1. Create a new PyCharm project (or open an existing one).
2. Copy this whole file into a file called app.py
3. Open the Terminal tab at the bottom of PyCharm and run:
       pip install flask
4. Right-click this file and choose "Run 'app'" (or press the green play button).
5. Open the link it prints in your terminal (usually http://127.0.0.1:5000)

OPTIONAL - Email notifications when someone submits a form:
- Install flask-mail:  pip install flask-mail python-dotenv
- Fill in MAIL_USERNAME, MAIL_PASSWORD, NOTIFY_EMAIL below.
- If left blank, the site still works fine - it just skips sending email
  and only saves the lead to the database (site.db).

WHATSAPP:
- Change WHATSAPP_NUMBER below to your own number (country code, no + or spaces).
  Example: South African number 082 123 4567 -> "27821234567"
"""

import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, render_template_string, g

# ---------------------------------------------------------------------------
# CONFIG - edit these values for your business
# ---------------------------------------------------------------------------
BUSINESS_NAME = "Lahshishi Marketing Agency"
TAGLINE = "We take your business to the higher level"
WHATSAPP_NUMBER = "0672281091"   # <-- put your real WhatsApp number here
DATABASE = "site.db"

# Optional email settings - leave blank to disable email notifications
MAIL_USERNAME = ""      # e.g. "youremail@gmail.com"
MAIL_PASSWORD = ""      # e.g. Gmail App Password
NOTIFY_EMAIL = ""       # where you want to receive lead notifications

app = Flask(__name__)

# ---------------------------------------------------------------------------
# DATABASE HELPERS (using plain SQLite - no extra libraries needed)
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            service TEXT,
            details TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_lead(name, phone, email, service, details):
    db = get_db()
    db.execute(
        "INSERT INTO leads (name, phone, email, service, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, phone, email, service, details, datetime.now().isoformat())
    )
    db.commit()
    maybe_send_email(name, phone, email, service, details)

def maybe_send_email(name, phone, email, service, details):
    """Sends an email notification only if credentials are filled in above."""
    if not MAIL_USERNAME or not MAIL_PASSWORD or not NOTIFY_EMAIL:
        return  # email not configured - skip silently
    try:
        import smtplib
        from email.mime.text import MIMEText

        body = f"New lead ({service})\n\nName: {name}\nPhone: {phone}\nEmail: {email}\nDetails: {details}"
        msg = MIMEText(body)
        msg["Subject"] = f"New website lead: {service}"
        msg["From"] = MAIL_USERNAME
        msg["To"] = NOTIFY_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[Email notification failed - lead was still saved] {e}")

# ---------------------------------------------------------------------------
# SHARED PAGE LAYOUT (base template)
# ---------------------------------------------------------------------------
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ business_name }} - {{ page_title }}</title>
    <style>
        :root {
            --gold: #e8a765;
            --black: #0d0d0d;
            --panel: #1a1a1a;
            --text-light: #f2f2f2;
        }
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: var(--black); color: var(--text-light); }
        nav { background: #000; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #2a2a2a; }
        .brand-group { display: flex; align-items: center; gap: 12px; }
        .brand-group img { height: 44px; width: auto; }
        .brand { font-size: 19px; font-weight: bold; color: var(--gold); letter-spacing: 0.5px; }
        nav .links a { color: #ddd; text-decoration: none; margin-left: 20px; font-weight: 500; font-size: 15px; }
        nav .links a:hover { color: var(--gold); }
        .container { max-width: 800px; margin: 50px auto; padding: 0 20px; }
        h1 { color: var(--gold); font-weight: 700; }
        h2 { color: var(--text-light); }
        p, li { color: #cfcfcf; line-height: 1.6; }
        .tagline { color: #aaa; font-style: italic; margin-top: -10px; }
        .card {
            background: var(--panel); padding: 26px; border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.4); margin-bottom: 20px;
            border: 1px solid #2a2a2a;
        }
        .card a { color: var(--gold); text-decoration: none; }
        .card a:hover { text-decoration: underline; }
        form { display: flex; flex-direction: column; gap: 12px; max-width: 420px; }
        input, textarea {
            padding: 11px; border: 1px solid #333; border-radius: 6px; font-size: 15px;
            background: #111; color: #fff;
        }
        input::placeholder, textarea::placeholder { color: #888; }
        button {
            background: var(--gold); color: #111; padding: 12px; border: none;
            border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: bold;
        }
        button:hover { background: #f2ba85; }
        .success { color: #6fdc8c; font-weight: bold; margin-top: 10px; }
        .service-card { border-left: 3px solid var(--gold); }
        .whatsapp-btn {
            position: fixed; bottom: 20px; right: 20px; background: var(--gold); color: #111;
            padding: 14px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;
            letter-spacing: 0.5px; box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .whatsapp-btn:hover { background: #f2ba85; }
        footer { text-align: center; padding: 30px; color: #666; font-size: 13px; border-top: 1px solid #222; margin-top: 40px; }
    </style>
</head>
<body>
    <nav>
        <div class="brand-group">
            <img src="/static/images/logo.jpg" alt="{{ business_name }} logo">
        </div>
        <div class="links">
            <a href="/">Home</a>
            <a href="/sell-car">Sell Your Car</a>
            <a href="/graphic-design">Graphic Design</a>
            <a href="/course">Course</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>

    <div class="container">
        {{ content|safe }}
    </div>

    <a class="whatsapp-btn" href="https://wa.me/{{ whatsapp }}" target="_blank">WhatsApp Us</a>

    <footer>&copy; {{ year }} {{ business_name }}. All rights reserved.</footer>
</body>
</html>
"""

def render_page(page_title, content):
    return render_template_string(
        BASE_TEMPLATE,
        business_name=BUSINESS_NAME,
        page_title=page_title,
        content=content,
        whatsapp=WHATSAPP_NUMBER,
        year=datetime.now().year
    )

# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    content = """
    <div class="card">
        <h1>Sell Your Car Fast. Look Sharp. Build Your Business.</h1>
        <p class="tagline">We take your business to the higher level.</p>
        <p>We help you sell your car quickly, design standout graphics for your brand,
           and teach you how to build a business through our entrepreneurial course.</p>
    </div>
    <div class="card service-card"><a href="/sell-car"><h2>Sell Your Car</h2></a><p>Get a fast, hassle-free sale.</p></div>
    <div class="card service-card"><a href="/graphic-design"><h2>Graphic Design</h2></a><p>Logos, flyers, social media content and more.</p></div>
    <div class="card service-card"><a href="/course"><h2>Entrepreneurial Course</h2></a><p>Learn how to start and grow your own business.</p></div>
    """
    return render_page("Home", content)


@app.route("/sell-car", methods=["GET", "POST"])
def sell_car():
    success = False
    if request.method == "POST":
        save_lead(
            request.form.get("name"),
            request.form.get("phone"),
            request.form.get("email"),
            "sell_car",
            request.form.get("car_details")
        )
        success = True

    content = """
    <h1>Sell Your Car Fast</h1>
    <p>Fill in your car details below and we'll be in touch shortly.</p>
    <div class="card">
        <form method="POST">
            <input type="text" name="name" placeholder="Your Full Name" required>
            <input type="tel" name="phone" placeholder="Phone Number" required>
            <input type="email" name="email" placeholder="Email (optional)">
            <textarea name="car_details" rows="4" placeholder="Car Make, Model, Year, Asking Price" required></textarea>
            <button type="submit">Submit</button>
        </form>
        {% if success %}<p class="success">Thank you. We'll contact you shortly.</p>{% endif %}
    </div>
    """
    content = render_template_string(content, success=success)
    return render_page("Sell Your Car", content)


@app.route("/graphic-design")
def graphic_design():
    content = """
    <h1>Graphic Design Services</h1>
    <div class="card">
        <p>We design logos, flyers, business cards, and social media content that make your brand stand out.</p>
        <ul>
            <li>Logo Design</li>
            <li>Social Media Graphics</li>
            <li>Flyers & Posters</li>
            <li>Business Branding Packages</li>
        </ul>
        <p>Message us on WhatsApp to discuss your project and get a quote.</p>
    </div>
    """
    return render_page("Graphic Design", content)


@app.route("/course")
def course():
    content = """
    <h1>Entrepreneurial Course</h1>
    <div class="card">
        <p>Learn the practical steps to start, market, and grow your own business - taught from real experience.</p>
        <ul>
            <li>Finding and validating a business idea</li>
            <li>Marketing on a small budget</li>
            <li>Basic financial management</li>
            <li>Building a brand people trust</li>
        </ul>
        <p>Contact us on WhatsApp or via the contact page to enrol.</p>
    </div>
    """
    return render_page("Entrepreneurial Course", content)


@app.route("/about")
def about():
    content = """
    <h1>About Us</h1>
    <div class="card">
        <p>We're a marketing agency helping everyday people sell their cars faster,
           build stronger visual brands, and start their own businesses with confidence.</p>
    </div>
    """
    return render_page("About", content)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    success = False
    if request.method == "POST":
        save_lead(
            request.form.get("name"),
            request.form.get("phone"),
            request.form.get("email"),
            "general_contact",
            request.form.get("message")
        )
        success = True

    content = """
    <h1>Contact Us</h1>
    <div class="card">
        <form method="POST">
            <input type="text" name="name" placeholder="Your Full Name" required>
            <input type="tel" name="phone" placeholder="Phone Number" required>
            <input type="email" name="email" placeholder="Email (optional)">
            <textarea name="message" rows="4" placeholder="Your Message" required></textarea>
            <button type="submit">Send</button>
        </form>
        {% if success %}<p class="success">Message sent. We'll get back to you soon.</p>{% endif %}
    </div>
    """
    content = render_template_string(content, success=success)
    return render_page("Contact", content)


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

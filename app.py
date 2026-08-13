"""
Lahshishi Marketing Agency - Official Website (based on poster design)
------------------------------------------------------------------------
HOW TO RUN IN PYCHARM:
1. Copy this whole file into a file called app.py in a new PyCharm project
2. In the Terminal tab, run:  pip install flask
3. Right-click this file -> Run 'app'
4. Open the link it prints (usually http://127.0.0.1:5000)

Don't forget: put your logo file at static/images/logo.jpg (same as before)
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, render_template_string, g

# ---------------------------------------------------------------------------
# CONFIG - matches the poster
# ---------------------------------------------------------------------------
BUSINESS_NAME = "Lahshishi Marketing Agency"
TAGLINE = "We take your business to the higher level"
PHONE_DISPLAY = "067 288 1091"
WHATSAPP_NUMBER = "27672881091"   # 067 288 1091 converted to international format
EMAIL = "lma.businessgrowth@gmail.com"
DATABASE = "site.db"

# Optional email notifications - fill in later if you want form submissions emailed to you
# Optional email notifications - set these as Environment Variables on Render,
# never write your real password directly in this file once it's on GitHub.
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# DATABASE HELPERS
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
    maybe_send_thank_you(name, email)

def maybe_send_email(name, phone, email, service, details):
    if not MAIL_USERNAME or not MAIL_PASSWORD or not NOTIFY_EMAIL:
        return
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

def maybe_send_thank_you(name, email):
    """Sends an automatic thank-you email to the customer, with a link to WhatsApp."""
    if not MAIL_USERNAME or not MAIL_PASSWORD or not email:
        return  # no email configured, or customer didn't leave an email - skip silently
    try:
        import smtplib
        from email.mime.text import MIMEText

        first_name = (name or "there").split(" ")[0]
        whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}"

        body = (
            f"Hi {first_name},\n\n"
            f"Thank you for reaching out to {BUSINESS_NAME}. We've received your message "
            f"and a member of our team will get back to you shortly.\n\n"
            f"If you'd like to chat with us right away, click the link below to message us "
            f"directly on WhatsApp:\n\n"
            f"{whatsapp_link}\n\n"
            f"{TAGLINE}.\n\n"
            f"Kind regards,\n"
            f"{BUSINESS_NAME}"
        )
        msg = MIMEText(body)
        msg["Subject"] = f"Thanks for reaching out to {BUSINESS_NAME}"
        msg["From"] = MAIL_USERNAME
        msg["To"] = email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[Thank-you email failed - lead was still saved] {e}")

# ---------------------------------------------------------------------------
# SERVICES (from the poster)
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "title": "Social Media Management",
        "text": "We manage your social platforms to build engagement and grow your brand."
    },
    {
        "title": "Business Content Creation",
        "text": "High-quality content and advertisement videos that capture attention and drive results."
    },
    {
        "title": "Website Design & Management",
        "text": "Modern, responsive websites that represent your brand and convert visitors into customers."
    },
    {
        "title": "Business Registration",
        "text": "We help you register your business the right way and get you officially established."
    },
    {
        "title": "Business Growth Strategies",
        "text": "Proven strategies to increase your visibility, attract more customers, and grow your business."
    },
]

# ---------------------------------------------------------------------------
# PAGE TEMPLATE
# ---------------------------------------------------------------------------
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="v2LWsbfodM08U3P8dIevdQv91YLXhM3PsdjZvUaIiUI" />
    <meta name="description" content="Lahshishi Marketing Agency helps businesses grow through social media management, content creation, website design, business registration, and growth strategies.">
    <meta name="keywords" content="marketing agency, social media management, content creation, website design, business registration, business growth strategies, South Africa">
    <meta property="og:title" content="{{ business_name }} - We Take Your Business To The Higher Level">
    <meta property="og:description" content="Social media management, content creation, website design, business registration, and growth strategies - all in one place.">
    <meta property="og:type" content="website">
    <title>{{ business_name }}</title>
    <style>
        :root {
            --orange: #d4af37;
            --orange-light: #e8c766;
            --black: #0a0a0a;
            --panel: #161616;
            --text-light: #f2f2f2;
            --text-muted: #b8b8b8;
        }
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: var(--black); color: var(--text-light); }

        nav {
            background: #000; padding: 16px 32px; display: flex; justify-content: space-between;
            align-items: center; flex-wrap: wrap; border-bottom: 1px solid #262626;
            position: sticky; top: 0; z-index: 10;
        }
        nav img { height: 46px; width: auto; }
        nav .links a { color: #ddd; text-decoration: none; margin-left: 22px; font-weight: 500; font-size: 15px; }
        nav .links a:hover { color: var(--orange); }

        .hero {
            max-width: 1000px; margin: 0 auto; padding: 70px 24px 50px; text-align: center;
        }
        .hero h1 { font-size: 40px; line-height: 1.25; margin-bottom: 10px; }
        .hero h1 .highlight { color: var(--orange); }
        .hero p.tagline { color: var(--orange-light); font-style: italic; font-size: 16px; margin-top: 0; }
        .hero p.description { max-width: 600px; margin: 20px auto 0; color: var(--text-muted); font-size: 16px; line-height: 1.7; }

        .section { max-width: 1000px; margin: 0 auto; padding: 40px 24px; }
        .section-label {
            display: inline-block; background: var(--orange); color: #111; font-weight: bold;
            padding: 8px 20px; border-radius: 4px; font-size: 14px; letter-spacing: 0.5px; margin-bottom: 30px;
        }

        html { scroll-behavior: smooth; }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
        .service-card {
            background: var(--panel); border: 1px solid #262626; border-left: 3px solid var(--orange);
            border-radius: 8px; padding: 24px; cursor: pointer;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }
        .service-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.15);
            border-color: var(--orange);
        }
        .service-card.selected {
            border-color: var(--orange); box-shadow: 0 0 0 1px var(--orange);
            background: #1c1706;
        }
        .service-card h3 { margin: 0 0 10px; color: var(--text-light); font-size: 18px; display: flex; align-items: center; justify-content: space-between; }
        .service-card h3 .arrow { color: var(--orange); font-size: 18px; opacity: 0; transition: opacity 0.2s ease, transform 0.2s ease; transform: translateX(-4px); }
        .service-card:hover h3 .arrow { opacity: 1; transform: translateX(0); }
        .service-card p { margin: 0; color: var(--text-muted); font-size: 14.5px; line-height: 1.6; }

        .promise-strip {
            display: flex; justify-content: center; gap: 50px; flex-wrap: wrap;
            padding: 30px 24px; border-top: 1px solid #262626; border-bottom: 1px solid #262626;
            text-align: center;
        }
        .promise-strip .item span { display: block; color: var(--orange); font-weight: bold; font-size: 15px; }

        .cta-box {
            max-width: 1000px; margin: 50px auto; padding: 26px 30px; border: 1px solid var(--orange);
            border-radius: 10px; text-align: center;
        }
        .cta-box h2 { color: var(--orange); margin: 0 0 8px; font-size: 22px; }
        .cta-box p { color: var(--text-muted); margin: 0; }

        form { display: flex; flex-direction: column; gap: 12px; max-width: 460px; margin: 0 auto; }
        input, textarea {
            padding: 12px; border: 1px solid #333; border-radius: 6px; font-size: 15px;
            background: #111; color: #fff;
        }
        input::placeholder, textarea::placeholder { color: #888; }
        button {
            background: var(--orange); color: #111; padding: 13px; border: none;
            border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: bold;
        }
        button:hover { background: var(--orange-light); }
        .success-msg { color: #7fd88f; font-weight: bold; text-align: center; }

        .contact-info {
            display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
            margin: 30px auto; text-align: center;
        }
        .contact-info div span { display: block; color: var(--text-muted); font-size: 13px; }
        .contact-info div strong { color: var(--orange); font-size: 16px; }

        .whatsapp-btn {
            position: fixed; bottom: 20px; right: 20px; background: var(--orange); color: #111;
            padding: 14px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;
            letter-spacing: 0.5px; box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .whatsapp-btn:hover { background: var(--orange-light); }

        .footer-banner {
            background: var(--orange); color: #111; text-align: center; padding: 16px;
            font-weight: bold; letter-spacing: 0.5px; margin-top: 40px;
        }
        footer.copyright { text-align: center; padding: 24px; color: #666; font-size: 13px; }
    </style>
</head>
<body>
    <nav>
        <img src="/static/images/logo.jpg" alt="{{ business_name }} logo">
        <div class="links">
            <a href="/#services">Services</a>
            <a href="/#about">About</a>
            <a href="/#contact">Contact</a>
        </div>
    </nav>

    {{ content|safe }}

    <a class="whatsapp-btn" href="https://wa.me/{{ whatsapp }}" target="_blank">WhatsApp Us</a>

    <div class="footer-banner">YOUR SUCCESS IS OUR MISSION</div>
    <footer class="copyright">&copy; {{ year }} {{ business_name }}. All rights reserved.</footer>
</body>
</html>
"""

def render_page(content):
    return render_template_string(
        PAGE_TEMPLATE,
        business_name=BUSINESS_NAME,
        content=content,
        whatsapp=WHATSAPP_NUMBER,
        year=datetime.now().year
    )

# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    success = False
    if request.method == "POST":
        save_lead(
            request.form.get("name"),
            request.form.get("phone"),
            request.form.get("email"),
            "contact_form",
            request.form.get("message")
        )
        success = True

    services_html = "".join(
        f'<div class="service-card" onclick="selectService(\'{s["title"]}\', this)">'
        f'<h3>{s["title"]}<span class="arrow">&#8594;</span></h3>'
        f'<p>{s["text"]}</p></div>'
        for s in SERVICES
    )

    content = """
    <div class="hero">
        <p class="tagline">{{ tagline }}</p>
        <h1>We Boost <span class="highlight">Brands</span>.<br>We Grow <span class="highlight">Businesses</span>.</h1>
        <p class="description">
            We specialise in boosting brand presence and achieving marketing goals in order to increase more customers.
        </p>
    </div>

    <div class="promise-strip">
        <div class="item"><span>Strategy</span></div>
        <div class="item"><span>Creativity</span></div>
        <div class="item"><span>Results</span></div>
    </div>

    <div class="section" id="services">
        <div class="section-label">OUR SERVICES</div>
        <p style="color: var(--text-muted); margin-top: -16px; margin-bottom: 26px; font-size: 15px;">
            Click on what you need help with — we'll take you straight to the form.
        </p>
        <div class="services-grid">
            {{ services_html|safe }}
        </div>
    </div>

    <div class="cta-box" id="about">
        <h2>More Visibility. More Customers. More Growth.</h2>
        <p>Let's grow your brand together.</p>
    </div>

    <div class="section" id="contact">
        <div class="section-label">GET IN TOUCH</div>
        <p id="selected-service-note" style="color: var(--orange); font-weight: bold; display: none; margin-top: -16px; margin-bottom: 20px;"></p>
        <div class="contact-info">
            <div><span>Call or WhatsApp</span><strong>{{ phone }}</strong></div>
            <div><span>Email</span><strong>{{ email }}</strong></div>
        </div>
        <form method="POST">
            <input type="text" name="name" placeholder="Your Full Name" required>
            <input type="tel" name="phone" placeholder="Phone Number" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="hidden" name="interested_service" id="interested_service" value="">
            <textarea name="message" id="message-box" rows="4" placeholder="Tell us about your business and what you need" required></textarea>
            <button type="submit">Send Message</button>
        </form>
        {% if success %}<p class="success-msg">Thank you. We'll be in touch shortly.</p>{% endif %}
    </div>

    <script>
        function selectService(title, cardEl) {
            document.querySelectorAll('.service-card').forEach(function(c) {
                c.classList.remove('selected');
            });
            cardEl.classList.add('selected');

            document.getElementById('interested_service').value = title;

            var note = document.getElementById('selected-service-note');
            note.textContent = "You're enquiring about: " + title;
            note.style.display = 'block';

            var box = document.getElementById('message-box');
            if (!box.value) {
                box.value = "Hi, I'd like help with " + title + ". ";
            }

            document.getElementById('contact').scrollIntoView({ behavior: 'smooth', block: 'start' });
            setTimeout(function() { box.focus(); }, 500);
        }

        // Fade-in animation for sections as they scroll into view
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.15 });

        document.querySelectorAll('.service-card, .cta-box').forEach(function(el) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(16px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(el);
        });
    </script>
    """
    content = render_template_string(
        content,
        tagline=TAGLINE,
        services_html=services_html,
        phone=PHONE_DISPLAY,
        email=EMAIL,
        success=success
    )
    return render_page(content)


@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\nAllow: /\nSitemap: " + request.url_root + "sitemap.xml",
        200,
        {"Content-Type": "text/plain"}
    )

@app.route("/sitemap.xml")
def sitemap():
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>{request.url_root}</loc></url>
</urlset>"""
    return (xml, 200, {"Content-Type": "application/xml"})


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
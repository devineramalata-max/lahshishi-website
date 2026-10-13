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
def _icon(paths):
    """Wraps SVG shapes in a standard 24x24 gold line-icon."""
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>'
    )

ICONS = {
    "social": _icon('<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.5 8.5 0 0 1-3.8-.9L3 20l1.1-4.9A8.4 8.4 0 1 1 21 11.5z"/>'
                    '<path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01"/>'),
    "content": _icon('<rect x="2" y="6" width="13" height="12" rx="2"/><polygon points="22 8 15 12 22 16"/>'),
    "website": _icon('<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>'
                     '<path d="M12 2a15 15 0 0 1 0 20a15 15 0 0 1 0-20"/>'),
    "register": _icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
                      '<polyline points="14 2 14 8 20 8"/><polyline points="9 15 11 17 15 13"/>'),
    "growth": _icon('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
}

# Each service has a photo slot: put a JPG named "<slug>.jpg" in static/images/services/
# (e.g. static/images/services/social-media.jpg). If a photo is missing, the site
# simply shows the black-and-gold graphic instead, so nothing ever looks broken.
SERVICES = [
    {
        "slug": "social-media",
        "icon": "social",
        "title": "Social Media Management",
        "text": "We manage your social platforms to build engagement and grow your brand.",
        "lead": "Your brand, active and consistent on the platforms where your customers spend their time.",
        "includes": [
            "Content planning and scheduling",
            "Posting and page management",
            "Community engagement and replies",
            "Brand-consistent look and tone",
            "Growth-focused page strategy",
        ],
    },
    {
        "slug": "content-creation",
        "icon": "content",
        "title": "Business Content Creation",
        "text": "High-quality content and advertisement videos that capture attention and drive results.",
        "lead": "Photos, videos and adverts that make people stop scrolling and take notice of your business.",
        "includes": [
            "Advertisement videos",
            "Product and service content",
            "Social-media-ready graphics",
            "Promotional campaign content",
            "Messaging that fits your brand",
        ],
    },
    {
        "slug": "website-design",
        "icon": "website",
        "title": "Website Design & Management",
        "text": "Modern, responsive websites that represent your brand and convert visitors into customers.",
        "lead": "A professional website that looks sharp on every device and turns visitors into enquiries.",
        "includes": [
            "Modern, mobile-friendly design",
            "Contact and enquiry forms",
            "Search-engine (Google) setup",
            "Hosting and going live",
            "Ongoing updates and management",
        ],
    },
    {
        "slug": "business-registration",
        "icon": "register",
        "title": "Business Registration",
        "text": "We help you register your business the right way and get you officially established.",
        "lead": "Get your business officially established, with the paperwork handled the right way from day one.",
        "includes": [
            "Guidance on the right business structure",
            "Registration support",
            "Help with the required documents",
            "Getting you officially established",
        ],
    },
    {
        "slug": "business-growth",
        "icon": "growth",
        "title": "Business Growth Strategies",
        "text": "Proven strategies to increase your visibility, attract more customers, and grow your business.",
        "lead": "A clear plan to be seen by more people, win more customers and keep growing.",
        "includes": [
            "Marketing plan built around your goals",
            "Visibility and brand-awareness strategy",
            "Customer attraction campaigns",
            "Practical next steps you can act on",
        ],
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
        nav { padding-top: 10px; padding-bottom: 10px; }
        nav img { height: 74px; width: auto; display: block; }
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

        /* ---------- GRAPHICS ---------- */
        .hero-wrap { position: relative; overflow: hidden; }
        .hero-wrap .hero { position: relative; z-index: 2; padding-bottom: 80px; }
        .hero-glow {
            position: absolute; top: -140px; left: 50%; width: 720px; height: 720px;
            transform: translateX(-50%); z-index: 0; pointer-events: none;
            background: radial-gradient(circle, rgba(212,175,55,0.20) 0%, rgba(212,175,55,0) 62%);
            animation: glowPulse 7s ease-in-out infinite;
        }
        .hero-chart {
            position: absolute; left: 0; bottom: 0; width: 100%; height: 78%;
            z-index: 1; opacity: 0.55; pointer-events: none;
        }
        .chart-line { stroke-dasharray: 1; stroke-dashoffset: 1; animation: drawLine 3.2s ease-out 0.4s forwards; filter: drop-shadow(0 0 6px rgba(212,175,55,0.7)); }
        .chart-area { opacity: 0; animation: fadeIn 1.6s ease-out 2.4s forwards; }
        .chart-dots circle { opacity: 0; animation: popIn 0.5s ease-out forwards; }
        .chart-dots circle:nth-child(1) { animation-delay: 1.0s; }
        .chart-dots circle:nth-child(2) { animation-delay: 1.7s; }
        .chart-dots circle:nth-child(3) { animation-delay: 2.3s; }
        .chart-dots circle:nth-child(4) { animation-delay: 2.9s; }
        .chart-dots .end-dot { animation: popIn 0.5s ease-out 3.4s forwards, endPulse 2.2s ease-in-out 4s infinite; transform-box: fill-box; transform-origin: center; }

        .hero-actions { display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; margin-top: 34px; }
        .btn-primary, .btn-ghost {
            padding: 13px 28px; border-radius: 4px; font-weight: bold; font-size: 15px;
            text-decoration: none; letter-spacing: 0.4px; transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
        }
        .btn-primary { background: var(--orange); color: #111; }
        .btn-primary:hover { background: var(--orange-light); transform: translateY(-2px); box-shadow: 0 8px 22px rgba(212,175,55,0.3); }
        .btn-ghost { border: 1px solid var(--orange); color: var(--orange); }
        .btn-ghost:hover { background: rgba(212,175,55,0.1); transform: translateY(-2px); }

        .hero-logo { display: block; width: min(340px, 72%); height: auto; margin: 0 auto 30px; }
        .hero-logo, .hero .tagline, .hero h1, .hero .description, .hero-actions { opacity: 0; animation: riseIn 0.8s ease-out forwards; }
        .hero-logo { animation-delay: 0.05s; }
        .hero .tagline { animation-delay: 0.1s; }
        .hero h1 { animation-delay: 0.25s; }
        .hero .description { animation-delay: 0.4s; }
        .hero-actions { animation-delay: 0.55s; }

        .promise-strip .item { display: flex; align-items: center; gap: 12px; }
        .promise-strip .item svg { width: 26px; height: 26px; color: var(--orange); }
        .promise-strip .item span { font-size: 16px; letter-spacing: 1px; text-transform: uppercase; }

        .icon-badge {
            width: 48px; height: 48px; border-radius: 12px; margin-bottom: 16px;
            display: flex; align-items: center; justify-content: center; color: var(--orange);
            background: rgba(212,175,55,0.10); border: 1px solid rgba(212,175,55,0.25);
            transition: transform 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
        }
        .icon-badge svg { width: 26px; height: 26px; }
        .service-card:hover .icon-badge {
            transform: scale(1.1) rotate(-4deg); background: rgba(212,175,55,0.2);
            box-shadow: 0 0 22px rgba(212,175,55,0.35);
        }

        /* ---------- SERVICE CARDS WITH PHOTO BACKGROUNDS ---------- */
        .service-card {
            position: relative; overflow: hidden; min-height: 290px;
            display: flex; flex-direction: column; justify-content: flex-end;
            background-color: #121212;
            background-image:
                linear-gradient(180deg, rgba(10,10,10,0.35) 0%, rgba(10,10,10,0.92) 78%),
                var(--photo),
                radial-gradient(circle at 80% 15%, rgba(212,175,55,0.22), rgba(212,175,55,0) 60%);
            background-size: cover; background-position: center;
        }
        .service-card .icon-badge { margin-bottom: auto; backdrop-filter: blur(4px); background: rgba(10,10,10,0.55); }
        .service-card p { color: #d6d6d6; }
        .service-card .more {
            margin-top: 14px; font-size: 13px; font-weight: bold; letter-spacing: 0.6px;
            color: var(--orange); text-transform: uppercase;
        }
        .service-card:focus-visible { outline: 2px solid var(--orange); outline-offset: 3px; }

        .reveal { opacity: 0; transform: translateY(16px);
            transition: opacity 0.5s ease, transform 0.5s ease, box-shadow 0.25s ease, border-color 0.25s ease; }
        .reveal.in { opacity: 1; transform: none; }
        .service-card.reveal.in:hover { transform: translateY(-6px); }

        /* ---------- SERVICE DETAIL PANEL ---------- */
        .svc-modal {
            position: fixed; inset: 0; z-index: 100; display: none; align-items: center; justify-content: center;
            padding: 24px; background: rgba(0,0,0,0.78); backdrop-filter: blur(6px);
        }
        .svc-modal.open { display: flex; animation: modalIn 0.25s ease; }
        .svc-panel {
            position: relative; width: min(940px, 100%); max-height: calc(100vh - 48px);
            display: flex; flex-direction: column; overflow: hidden;
            background: #0f0f0f; border: 1px solid rgba(212,175,55,0.4); border-radius: 14px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.7), 0 0 60px rgba(212,175,55,0.08);
            animation: panelIn 0.35s ease;
        }
        .svc-scroll { overflow-y: auto; }
        .svc-close {
            position: absolute; top: 14px; right: 14px; z-index: 5; width: 40px; height: 40px;
            border-radius: 50%; border: 1px solid rgba(212,175,55,0.5); background: rgba(10,10,10,0.7);
            color: var(--orange); font-size: 24px; line-height: 1; padding: 0; cursor: pointer;
        }
        .svc-close:hover { background: var(--orange); color: #111; }
        .svc-hero {
            position: relative; min-height: 270px; padding: 40px 40px 32px;
            display: flex; flex-direction: column; justify-content: flex-end;
            background-color: #151515; background-size: cover; background-position: center;
        }
        .svc-hero-icon { flex: none; margin-bottom: auto; width: 56px; height: 56px; color: var(--orange);
            padding: 12px; border-radius: 14px; background: rgba(10,10,10,0.6); border: 1px solid rgba(212,175,55,0.35); }
        .svc-hero-icon + .svc-kicker { margin-top: 22px; }
        .svc-hero-icon svg { width: 100%; height: 100%; }
        .svc-kicker { color: var(--orange); font-size: 12px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold; margin: 0 0 8px; }
        .svc-hero h2 { margin: 0 0 10px; font-size: 34px; line-height: 1.2; color: #fff; }
        .svc-lead { margin: 0; max-width: 560px; color: #dcdcdc; font-size: 16px; line-height: 1.6; }
        .svc-body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 30px; padding: 32px 40px 38px; }
        .svc-body h3 { margin: 0 0 14px; color: var(--orange); font-size: 14px; letter-spacing: 1.2px; text-transform: uppercase; }
        .svc-body ul { list-style: none; margin: 0; padding: 0; }
        .svc-body li { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #222; color: #e4e4e4; font-size: 15px; }
        .svc-body li::before { content: ""; flex: none; width: 8px; height: 8px; margin-top: 7px; border-radius: 50%; background: var(--orange); box-shadow: 0 0 10px rgba(212,175,55,0.6); }
        .svc-side { background: #151515; border: 1px solid #262626; border-radius: 12px; padding: 22px; align-self: start; }
        .svc-side p { margin: 0 0 16px; color: var(--text-muted); font-size: 14.5px; line-height: 1.6; }
        .svc-side button, .svc-side a { display: block; width: 100%; text-align: center; margin-top: 10px; padding: 13px; border-radius: 6px; font-size: 15px; font-weight: bold; text-decoration: none; cursor: pointer; }
        .svc-whatsapp { border: 1px solid var(--orange); color: var(--orange); background: transparent; }
        .svc-whatsapp:hover { background: rgba(212,175,55,0.1); }
        .svc-next { background: transparent; border: 1px solid #333; color: #ccc; }
        .svc-next:hover { border-color: var(--orange); color: var(--orange); background: transparent; }
        body.modal-open { overflow: hidden; }

        @media (max-width: 720px) {
            .svc-modal { padding: 0; }
            .svc-panel { width: 100%; max-height: 100vh; height: 100%; border-radius: 0; border: none; }
            .svc-hero { min-height: 240px; padding: 28px 22px 24px; }
            .svc-hero h2 { font-size: 26px; }
            .svc-body { grid-template-columns: 1fr; padding: 24px 22px 32px; }
            .service-card { min-height: 250px; }
        }

        @keyframes modalIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes panelIn { from { opacity: 0; transform: translateY(26px) scale(0.97); } to { opacity: 1; transform: none; } }
        @keyframes drawLine { to { stroke-dashoffset: 0; } }
        @keyframes fadeIn { to { opacity: 1; } }
        @keyframes popIn { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }
        @keyframes endPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.5); } }
        @keyframes glowPulse { 0%, 100% { opacity: 0.7; } 50% { opacity: 1; } }
        @keyframes riseIn { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 640px) {
            .hero h1 { font-size: 30px; }
            .hero-chart { height: 55%; opacity: 0.4; }
            nav { padding: 8px 16px; }
            nav img { height: 58px; }
            .hero-logo { width: min(280px, 78%); }
            nav .links a { margin-left: 14px; font-size: 14px; }
        }
        @media (prefers-reduced-motion: reduce) {
            .reveal { opacity: 1; transform: none; transition: none; }
            .svc-modal.open, .svc-panel { animation: none; }
            .hero-glow, .chart-line, .chart-area, .chart-dots circle, .chart-dots .end-dot,
            .hero-logo, .hero .tagline, .hero h1, .hero .description, .hero-actions {
                animation: none !important; opacity: 1 !important; stroke-dashoffset: 0 !important;
            }
        }
    </style>
</head>
<body>
    <nav>
        <a href="/" aria-label="{{ business_name }} home">
            <img src="/static/images/logo-transparent.png" alt="{{ business_name }} logo"
                 onerror="this.onerror=null;this.src='/static/images/logo.jpg'">
        </a>
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
        f'<div class="service-card" role="button" tabindex="0" data-index="{i}" '
        f'aria-label="Open {s["title"]}" style="--photo:url(/static/images/services/{s["slug"]}.jpg)">'
        f'<div class="icon-badge">{ICONS[s["icon"]]}</div>'
        f'<h3>{s["title"]}<span class="arrow">&#8594;</span></h3>'
        f'<p>{s["text"]}</p>'
        f'<span class="more">View details</span></div>'
        for i, s in enumerate(SERVICES)
    )

    # Data handed to the browser so the detail panel can fill itself in
    services_data = [
        {
            "slug": s["slug"], "title": s["title"], "lead": s["lead"],
            "includes": s["includes"], "icon": ICONS[s["icon"]],
        }
        for s in SERVICES
    ]

    content = """
    <div class="hero-wrap">
        <div class="hero-glow"></div>
        <svg class="hero-chart" viewBox="0 0 1000 400" preserveAspectRatio="none" aria-hidden="true">
            <defs>
                <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#d4af37" stop-opacity="0.28"/>
                    <stop offset="100%" stop-color="#d4af37" stop-opacity="0"/>
                </linearGradient>
            </defs>
            <g class="grid-lines" stroke="#d4af37" stroke-opacity="0.08">
                <line x1="0" y1="100" x2="1000" y2="100"/>
                <line x1="0" y1="200" x2="1000" y2="200"/>
                <line x1="0" y1="300" x2="1000" y2="300"/>
            </g>
            <path class="chart-area" d="M0,330 L120,300 L240,315 L360,240 L480,260 L600,180 L720,200 L840,110 L1000,40 L1000,400 L0,400 Z" fill="url(#areaFill)"/>
            <path class="chart-line" d="M0,330 L120,300 L240,315 L360,240 L480,260 L600,180 L720,200 L840,110 L1000,40"
                  fill="none" stroke="#d4af37" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/>
            <g class="chart-dots" fill="#0a0a0a" stroke="#d4af37" stroke-width="3">
                <circle cx="120" cy="300" r="6"/><circle cx="360" cy="240" r="6"/>
                <circle cx="600" cy="180" r="6"/><circle cx="840" cy="110" r="6"/>
                <circle class="end-dot" cx="1000" cy="40" r="8" fill="#d4af37"/>
            </g>
        </svg>

        <div class="hero">
            <img class="hero-logo" src="/static/images/logo-transparent.png" alt="{{ tagline }}"
                 onerror="this.onerror=null;this.src='/static/images/logo.jpg'">
            <h1>We Boost <span class="highlight">Brands</span>.<br>We Grow <span class="highlight">Businesses</span>.</h1>
            <p class="description">
                We specialise in boosting brand presence and achieving marketing goals in order to increase more customers.
            </p>
            <div class="hero-actions">
                <a class="btn-primary" href="#services">Explore Services</a>
                <a class="btn-ghost" href="#contact">Get In Touch</a>
            </div>
        </div>
    </div>

    <div class="promise-strip">
        <div class="item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>
            <span>Strategy</span>
        </div>
        <div class="item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 17l.7 1.8 1.8.7-1.8.7L19 22l-.7-1.8-1.8-.7 1.8-.7z"/></svg>
            <span>Creativity</span>
        </div>
        <div class="item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/></svg>
            <span>Results</span>
        </div>
    </div>

    <div class="section" id="services">
        <div class="section-label">OUR SERVICES</div>
        <p style="color: var(--text-muted); margin-top: -16px; margin-bottom: 26px; font-size: 15px;">
            Tap a service to see exactly what's included, then request it in one click.
        </p>
        <div class="services-grid">
            {{ services_html|safe }}
        </div>
    </div>

    <div class="svc-modal" id="svc-modal" aria-hidden="true">
        <div class="svc-panel" role="dialog" aria-modal="true" aria-labelledby="svc-title">
            <button class="svc-close" id="svc-close" type="button" aria-label="Close">&times;</button>
            <div class="svc-scroll">
                <div class="svc-hero" id="svc-hero">
                    <div class="svc-hero-icon" id="svc-icon"></div>
                    <p class="svc-kicker">Lahshishi Marketing Agency</p>
                    <h2 id="svc-title"></h2>
                    <p class="svc-lead" id="svc-lead"></p>
                </div>
                <div class="svc-body">
                    <div>
                        <h3>What's included</h3>
                        <ul id="svc-list"></ul>
                    </div>
                    <div class="svc-side">
                        <p>Ready to get started? Send us your details and we'll get back to you shortly.</p>
                        <button type="button" id="svc-request">Request this service</button>
                        <a class="svc-whatsapp" id="svc-whatsapp" href="#" target="_blank" rel="noopener">Chat on WhatsApp</a>
                        <button type="button" class="svc-next" id="svc-next">Next service &#8594;</button>
                    </div>
                </div>
            </div>
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

        // ---------- Service detail panel ----------
        var SERVICES_DATA = {{ services_data|tojson }};
        var WA_NUMBER = {{ whatsapp|tojson }};
        var currentIndex = -1;
        var lastFocused = null;
        var modal = document.getElementById('svc-modal');

        function openService(i) {
            var s = SERVICES_DATA[i];
            if (!s) { return; }
            currentIndex = i;

            var photo = "url('/static/images/services/" + s.slug + ".jpg')";
            document.getElementById('svc-hero').style.backgroundImage =
                'linear-gradient(180deg, rgba(10,10,10,0.35) 0%, rgba(15,15,15,0.97) 100%), ' + photo + ', ' +
                'radial-gradient(circle at 80% 20%, rgba(212,175,55,0.28), rgba(212,175,55,0) 60%)';
            document.getElementById('svc-icon').innerHTML = s.icon;
            document.getElementById('svc-title').textContent = s.title;
            document.getElementById('svc-lead').textContent = s.lead;

            var list = document.getElementById('svc-list');
            list.innerHTML = '';
            s.includes.forEach(function(item) {
                var li = document.createElement('li');
                li.textContent = item;
                list.appendChild(li);
            });

            document.getElementById('svc-whatsapp').href =
                'https://wa.me/' + WA_NUMBER + '?text=' +
                encodeURIComponent("Hi, I'd like help with " + s.title + ".");

            if (!modal.classList.contains('open')) { lastFocused = document.activeElement; }
            modal.classList.add('open');
            modal.setAttribute('aria-hidden', 'false');
            document.body.classList.add('modal-open');
            modal.querySelector('.svc-scroll').scrollTop = 0;
            document.getElementById('svc-close').focus();
        }

        function closeService() {
            modal.classList.remove('open');
            modal.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('modal-open');
            if (lastFocused && lastFocused.focus) { lastFocused.focus(); }
        }

        document.querySelectorAll('.service-card').forEach(function(card) {
            card.addEventListener('click', function() { openService(Number(card.dataset.index)); });
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openService(Number(card.dataset.index)); }
            });
        });

        document.getElementById('svc-close').addEventListener('click', closeService);
        modal.addEventListener('click', function(e) { if (e.target === modal) { closeService(); } });
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('open')) { closeService(); }
        });
        document.getElementById('svc-next').addEventListener('click', function() {
            openService((currentIndex + 1) % SERVICES_DATA.length);
        });
        document.getElementById('svc-request').addEventListener('click', function() {
            var card = document.querySelector('.service-card[data-index="' + currentIndex + '"]');
            var title = SERVICES_DATA[currentIndex].title;
            lastFocused = null;
            closeService();
            selectService(title, card);
        });

        // Fade-in animation for sections as they scroll into view
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        document.querySelectorAll('.service-card, .cta-box').forEach(function(el) {
            el.classList.add('reveal');
            observer.observe(el);
        });
    </script>
    """
    content = render_template_string(
        content,
        tagline=TAGLINE,
        services_html=services_html,
        services_data=services_data,
        whatsapp=WHATSAPP_NUMBER,
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
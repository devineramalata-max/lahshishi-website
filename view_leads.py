"""
View Leads - shows everyone who submitted a form on your website
-------------------------------------------------------------------
HOW TO USE:
1. Make sure this file (view_leads.py) is in the SAME folder as app.py
2. Right-click this file in PyCharm and choose "Run 'view_leads'"
3. It will print every lead that has been submitted so far.

You can run this anytime - it just reads the database, it doesn't change anything.
"""

import sqlite3

DATABASE = "site.db"

def view_leads():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No leads submitted yet.")
        return

    print(f"\n===== {len(rows)} Lead(s) Found =====\n")
    for row in rows:
        print(f"Date:    {row['created_at']}")
        print(f"Service: {row['service']}")
        print(f"Name:    {row['name']}")
        print(f"Phone:   {row['phone']}")
        print(f"Email:   {row['email']}")
        print(f"Details: {row['details']}")
        print("-" * 40)

if __name__ == "__main__":
    view_leads()

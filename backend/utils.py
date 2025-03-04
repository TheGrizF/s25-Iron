"""
Use this to create all the helper functions for the routes.
Keeps them organized so we can use them again if we need to.
"""

def normalize_email(email):
    email = email.lower().strip()
    name, domain = email.split("@")

    if "gmail" in domain or "google" in domain:
        name = name.split("+")[0]
        name = name.replace(".", "")

    return f"{name}@{domain}"
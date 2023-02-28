import re
import dns.resolver
from bson import ObjectId
import secrets

def is_valid_email(email):
    # Check if the email address is valid according to the email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    # Extract the domain name from the email address
    domain = email.split('@')[1]

    # Query the DNS server for the MX records of the domain
    try:
        dns.resolver.query(domain, 'MX')
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return False

    return True
def tagsValid(tags):
    if not re.match(r"^[a-zA-Z0-9, ]+$", tags):
        return False
    return True

def tag_search(tagstring):
    tags = tagstring.split(',')
    return [tag.strip() for tag in tags]

def generate_post_id():
    post_id = ObjectId()
    return str(post_id)

def secretCreate():
    session_secret = secrets.token_hex(16)
    return session_secret
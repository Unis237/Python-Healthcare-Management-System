import re

def validate_email(email):
    """Validate email format."""
    if email is None:
        return True
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def validate_phone_number(phone):
    """Validate phone number format: digits only, length 7 to 15."""
    if phone is None:
        return True
    phone = phone.strip()
    if phone == '':
        return True
    phone_regex = r'^\+?\d{7,15}$'
    return re.match(phone_regex, phone) is not None

def sanitize_text_input(text, max_length=255):
    """Sanitize text input by stripping and limiting length."""
    if text is None:
        return None
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text

def validate_id_format(id_str, prefix):
    """Validate ID format with expected prefix and pattern."""
    if id_str is None:
        return False
    id_str = id_str.strip()
    pattern = rf'^{prefix}-\d{{2}}-\d{{6}}$'
    return re.match(pattern, id_str) is not None

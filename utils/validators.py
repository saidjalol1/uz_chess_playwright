"""
Input validation module for email addresses.
"""

import re
from typing import Dict, Any


def validate_email(email: str) -> Dict[str, Any]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Dict with 'valid' (bool) and optional 'error' (str) keys
    """
    # Email validation regex pattern
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+'
    
    if re.match(pattern, email):
        return {'valid': True}
    else:
        return {
            'valid': False,
            'error': f'Invalid email format: "{email}". Email must contain @ symbol with characters before and after, and a domain with at least one dot.'
        }

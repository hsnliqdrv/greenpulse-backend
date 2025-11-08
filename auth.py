from functools import wraps
from flask import request, jsonify
from config import Config
from hmac import compare_digest


def require_api_key(f):
    """Decorator to require API key in X-API-Key header.

    Uses constant-time comparison to avoid timing attacks.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing API key'}), 401

        if not compare_digest(api_key, Config.API_KEY):
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)

    return decorated

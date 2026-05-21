"""WSGI entrypoint for Render and Gunicorn.

Expose a top-level `app` object so the default `gunicorn app:app`
command can import this module successfully.
"""

from backend.api.app import create_app

app = create_app()

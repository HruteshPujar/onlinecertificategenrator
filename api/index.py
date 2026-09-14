import os
import sys
import traceback
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from django.core.wsgi import get_wsgi_application
    django_application = get_wsgi_application()

    # Automatically run migrations on /tmp/db.sqlite3 if in ephemeral demo mode
    if os.getenv("VERCEL") and not os.getenv("DATABASE_URL"):
        from django.core.management import call_command
        try:
            call_command("migrate", interactive=False)
        except Exception as mig_err:
            print("Auto-migration notice:", mig_err, file=sys.stderr)

    def handler(environ, start_response):
        return django_application(environ, start_response)

    # Alias for Vercel
    app = handler

except Exception as e:
    error_traceback = traceback.format_exc()
    print("CRITICAL: Django WSGI initialization failed:", file=sys.stderr)
    print(error_traceback, file=sys.stderr)

    def handler(environ, start_response):
        status = "500 Internal Server Error"
        response_headers = [("Content-type", "text/plain; charset=utf-8")]
        start_response(status, response_headers)
        message = (
            "Django Initialization Failed on Vercel Serverless Function.\n\n"
            f"Traceback Details:\n{error_traceback}\n\n"
            "Please verify your environment variables (DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS) "
            "in the Vercel Dashboard Settings."
        )
        return [message.encode("utf-8")]

    app = handler

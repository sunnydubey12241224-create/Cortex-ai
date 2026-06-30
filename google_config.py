import os
import json

GOOGLE_CREDENTIALS = None

if os.getenv("GOOGLE_CREDENTIALS"):
    GOOGLE_CREDENTIALS = json.loads(
        os.getenv("GOOGLE_CREDENTIALS")
    )
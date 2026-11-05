import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
print("Mode:", os.getenv("MATRIX_MODE", "development"))
for key in ("DATABASE_URL", "API_KEY", "LOG_LEVEL", "ZION_ENDPOINT"):
    print(key, "configured" if os.getenv(key) else "missing: using default")

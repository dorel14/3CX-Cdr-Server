# Configuration centralisée
import os
CONFIG={
    "api": {
        "base_url": os.environ.get("API_BASE_URL", "http://localhost:8000"),
        "endpoints": {
            "cdr": "/v1/cdr",
            "cdr_details": "/v1/cdrdetails"
        }
    }
}
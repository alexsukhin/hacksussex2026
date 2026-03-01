from fastapi import Header, HTTPException

VALID_API_KEYS = {
    "arduino-zone1-key-abc123": "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e",
    "mock-zones-key-xyz789": "mock"
}

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
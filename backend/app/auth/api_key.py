import os

from fastapi import Header, HTTPException, status


# Validates the x-api-key header for protected API routes.
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected_api_key = os.getenv("API_KEY", "dev-secret-key")

    if x_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing API key.",
                    "details": None,
                }
            },
        )
"""
Error responses
"""
from __future__ import annotations

from typing import Any, Dict

from schemas.common import ErrorResponse

ResponsesDict = Dict[int, Dict[str, Any]]


def _retry_after_header() -> dict[str, Any]:
    return {
        "Retry-After": {
            "description": "Seconds to wait before retrying.",
            "schema": {"type": "integer", "example": 3600},
        }
    }


# common error
COMMON_ERROR_RESPONSES: ResponsesDict = {
    400: {"model": ErrorResponse, "description": "Bad request - Invalid parameters"},
    401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or expired token"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
    409: {"model": ErrorResponse, "description": "Conflict - Resource already exists"},
    429: {
        "model": ErrorResponse,
        "description": "Rate limit exceeded",
        "headers": _retry_after_header(),
    },
    422: {"model": ErrorResponse, "description": "Validation failed"},
}

# authentication error response
AUTH_REQUIRED_ERROR_RESPONSES: ResponsesDict = {
    401: COMMON_ERROR_RESPONSES[401],
    429: COMMON_ERROR_RESPONSES[429],
    422: COMMON_ERROR_RESPONSES[422],
}

# read error
READ_ERROR_RESPONSES: ResponsesDict = {
    401: COMMON_ERROR_RESPONSES[401],
    404: COMMON_ERROR_RESPONSES[404],
    429: COMMON_ERROR_RESPONSES[429],
    422: COMMON_ERROR_RESPONSES[422],
}

# ✅ 适合“创建资源”的接口：400/409/429/422（注册、创建 mood 等）
CREATE_ERROR_RESPONSES: ResponsesDict = {
    400: COMMON_ERROR_RESPONSES[400],
    409: COMMON_ERROR_RESPONSES[409],
    429: COMMON_ERROR_RESPONSES[429],
    422: COMMON_ERROR_RESPONSES[422],
}

# ✅ Auth 专用：登录/注册/刷新 token 常见错误组合
AUTH_ERROR_RESPONSES: ResponsesDict = {
    400: COMMON_ERROR_RESPONSES[400],
    401: COMMON_ERROR_RESPONSES[401],
    409: COMMON_ERROR_RESPONSES[409],
    429: COMMON_ERROR_RESPONSES[429],
    422: COMMON_ERROR_RESPONSES[422],
}

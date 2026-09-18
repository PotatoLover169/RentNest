from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Centralized REST API exception handler.

    Preserves DRF's existing error structure while adding
    consistent API metadata.
    """

    response = exception_handler(exc, context)

    if response is None:
        return response

    data = response.data

    # --------------------------------------------------------
    # Validation errors
    # --------------------------------------------------------

    if response.status_code == 400:
        payload = {
            "success": False,
            "message": "Validation failed.",
        }

        if isinstance(data, dict):
            payload.update(data)
        else:
            payload["detail"] = data

        return Response(
            payload,
            status=response.status_code,
            headers=response.headers,
        )

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if response.status_code == 401:
        return Response(
            {
                "success": False,
                "message": _extract_message(
                    data,
                    "Authentication credentials were not provided.",
                ),
            },
            status=response.status_code,
            headers=response.headers,
        )

    # --------------------------------------------------------
    # Permission denied
    # --------------------------------------------------------

    if response.status_code == 403:
        return Response(
            {
                "success": False,
                "message": _extract_message(
                    data,
                    "You do not have permission to perform this action.",
                ),
            },
            status=response.status_code,
            headers=response.headers,
        )

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    if response.status_code == 404:
        return Response(
            {
                "success": False,
                "message": _extract_message(
                    data,
                    "The requested resource was not found.",
                ),
            },
            status=response.status_code,
            headers=response.headers,
        )

    # --------------------------------------------------------
    # Other DRF exceptions
    # --------------------------------------------------------

    payload = {
        "success": False,
        "message": _extract_message(
            data,
            "An error occurred while processing the request.",
        ),
    }

    if isinstance(data, dict) and data:
        payload.update(data)

    return Response(
        payload,
        status=response.status_code,
        headers=response.headers,
    )


def _extract_message(data, default):
    """
    Extract a human-readable message from a DRF error response.
    """

    if isinstance(data, dict):
        detail = data.get("detail")

        if isinstance(detail, str):
            return detail

        if detail:
            return str(detail)

    if isinstance(data, str):
        return data

    return default
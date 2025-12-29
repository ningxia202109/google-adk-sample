import httpx
import json


def retrieve_service_documentation() -> str:
    """
    Fetch the OpenAPI specification (API documentation) from the local service.

    Returns:
        The API documentation as a JSON string.
    """
    try:
        response = httpx.get("http://127.0.0.1:6060/openapi.json")
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching API documentation: {str(e)}"


def execute_api_request(
    method: str, path: str, body_json: str = None, params_json: str = None
) -> str:
    """
    Execute a specific API request against the service.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE).
        path: API path (e.g., /users, /teams).
        body_json: Optional JSON string for the request body.
        params_json: Optional JSON string for query parameters.

    Returns:
        The API response as a string.
    """
    base_url = "http://127.0.0.1:6060"
    url = f"{base_url}{path}"

    body = None
    if body_json:
        try:
            body = json.loads(body_json)
        except json.JSONDecodeError:
            return f"Error: body_json must be a valid JSON string, got: {body_json}"

    params = None
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError:
            return f"Error: params_json must be a valid JSON string, got: {params_json}"

    try:
        with httpx.Client() as client:
            response = client.request(method, url, json=body, params=params)
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error executing API request: {str(e)}"

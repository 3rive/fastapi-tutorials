import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_preflight_allows_entitlements_mfe(client: AsyncClient) -> None:
    response = await client.options(
        "/entitlements",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in {
        "*",
        "http://localhost:5173",
    }

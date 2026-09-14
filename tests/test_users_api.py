import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_crud_flow(client: AsyncClient) -> None:
    create_response = await client.post(
        "/users",
        json={
            "email": "jane.doe@example.com",
            "full_name": "Jane Doe",
            "phone": "+15551234567",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["email"] == "jane.doe@example.com"
    assert created["full_name"] == "Jane Doe"
    user_id = created["id"]

    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == user_id

    list_response = await client.get("/users")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    patch_response = await client.patch(
        f"/users/{user_id}",
        json={"full_name": "Jane Q. Doe"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["full_name"] == "Jane Q. Doe"

    delete_response = await client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/users/{user_id}")
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_email_returns_conflict(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "full_name": "First User",
    }
    first = await client.post("/users", json=payload)
    assert first.status_code == 201
    second = await client.post("/users", json=payload)
    assert second.status_code == 409

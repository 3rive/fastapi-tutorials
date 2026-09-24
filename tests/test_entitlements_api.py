from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


def _grant_payload(**overrides):
    payload = {
        "automation_key": "incident_insights",
        "ad_group": "ssp-ops-admins",
        "permissions": ["view", "execute"],
        "granted_by": "alice.admin",
        "expires_at": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_entitlement_crud_flow(client: AsyncClient) -> None:
    create_response = await client.post("/entitlements", json=_grant_payload())
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["automation_key"] == "incident_insights"
    assert created["ad_group"] == "ssp-ops-admins"
    assert created["permissions"] == ["view", "execute"]
    assert created["status"] == "active"
    assert created["revoked_by"] is None
    assert created["revoked_at"] is None
    assert created["schema_version"] == 1
    entitlement_id = created["id"]

    get_response = await client.get(f"/entitlements/{entitlement_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == entitlement_id

    list_response = await client.get("/entitlements")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    patch_response = await client.patch(
        f"/entitlements/{entitlement_id}",
        json={"permissions": ["view"]},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["permissions"] == ["view"]

    revoke_response = await client.patch(
        f"/entitlements/{entitlement_id}",
        json={"status": "revoked", "revoked_by": "bob.admin"},
    )
    assert revoke_response.status_code == 200
    revoked = revoke_response.json()
    assert revoked["status"] == "revoked"
    assert revoked["revoked_by"] == "bob.admin"
    assert revoked["revoked_at"] is not None

    delete_response = await client.delete(f"/entitlements/{entitlement_id}")
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/entitlements/{entitlement_id}")
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_grant_returns_conflict(client: AsyncClient) -> None:
    payload = _grant_payload()
    first = await client.post("/entitlements", json=payload)
    assert first.status_code == 201
    second = await client.post("/entitlements", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_list_filters_by_status_and_automation(client: AsyncClient) -> None:
    first = await client.post("/entitlements", json=_grant_payload())
    assert first.status_code == 201
    second = await client.post(
        "/entitlements",
        json=_grant_payload(
            automation_key="cost_insights",
            ad_group="ssp-finance",
            permissions=["view"],
        ),
    )
    assert second.status_code == 201
    await client.patch(
        f"/entitlements/{second.json()['id']}",
        json={"status": "revoked", "revoked_by": "carol.admin"},
    )

    active = await client.get("/entitlements", params={"status": "active"})
    assert active.status_code == 200
    assert len(active.json()) == 1
    assert active.json()[0]["automation_key"] == "incident_insights"

    filtered = await client.get(
        "/entitlements",
        params={"automation_key": "cost_insights", "status": "revoked"},
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["ad_group"] == "ssp-finance"


@pytest.mark.asyncio
async def test_create_revoked_without_actor_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/entitlements",
        json=_grant_payload(status="revoked"),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_permission_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/entitlements",
        json=_grant_payload(permissions=["admin"]),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_unknown_entitlement_returns_not_found(client: AsyncClient) -> None:
    response = await client.get("/entitlements/64b64c2f2f8fb8c2a1e9d001")
    assert response.status_code == 404

import { beforeEach, describe, expect, it, vi } from "vitest";

import { EntitlementsApi, formatApiError } from "./api";

describe("formatApiError", () => {
  it("reads a string detail", () => {
    expect(formatApiError({ detail: "Entitlement not found" }, "fallback")).toBe(
      "Entitlement not found",
    );
  });

  it("joins validation messages", () => {
    expect(
      formatApiError(
        { detail: [{ msg: "Field required" }, { msg: "Invalid status" }] },
        "fallback",
      ),
    ).toBe("Field required; Invalid status");
  });
});

describe("EntitlementsApi", () => {
  const api = new EntitlementsApi("http://api.test");

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists grants with filters", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: "1", automation_key: "incident_insights" }],
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await api.list({
      automation_key: "incident_insights",
      status: "active",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/entitlements?automation_key=incident_insights&status=active",
      expect.objectContaining({ headers: expect.any(Object) }),
    );
    expect(result).toHaveLength(1);
  });

  it("creates a grant", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: "abc", status: "active" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await api.create({
      automation_key: "incident_insights",
      ad_group: "ssp-ops",
      granted_by: "alice",
      permissions: ["view"],
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/entitlements",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("raises API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({
          detail: "An entitlement already exists for this automation_key and ad_group",
        }),
      }),
    );

    await expect(
      api.create({
        automation_key: "incident_insights",
        ad_group: "ssp-ops",
        granted_by: "alice",
        permissions: ["view"],
      }),
    ).rejects.toThrow("An entitlement already exists for this automation_key and ad_group");
  });
});

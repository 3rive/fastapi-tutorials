import type {
  Entitlement,
  EntitlementCreate,
  EntitlementFilters,
  EntitlementUpdate,
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function formatApiError(payload: unknown, fallback: string): string {
  if (typeof payload !== "object" || payload === null || !("detail" in payload)) {
    return fallback;
  }
  const detail = (payload as { detail: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "object" && item !== null && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return String(item);
      })
      .join("; ");
  }
  return fallback;
}

export class EntitlementsApi {
  constructor(private readonly baseUrl: string) {}

  private resource(path = ""): string {
    const root = this.baseUrl.replace(/\/$/, "");
    return `${root}/entitlements${path}`;
  }

  async list(filters: EntitlementFilters = {}): Promise<Entitlement[]> {
    const params = new URLSearchParams();
    if (filters.automation_key) {
      params.set("automation_key", filters.automation_key);
    }
    if (filters.ad_group) {
      params.set("ad_group", filters.ad_group);
    }
    if (filters.status) {
      params.set("status", filters.status);
    }
    const query = params.toString();
    return this.request(query ? `${this.resource()}?${query}` : this.resource());
  }

  async create(payload: EntitlementCreate): Promise<Entitlement> {
    return this.request(this.resource(), {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async update(id: string, payload: EntitlementUpdate): Promise<Entitlement> {
    return this.request(this.resource(`/${id}`), {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  }

  async delete(id: string): Promise<void> {
    await this.request(this.resource(`/${id}`), { method: "DELETE" }, true);
  }

  private async request<T = Entitlement>(
    url: string,
    init: RequestInit = {},
    empty = false,
  ): Promise<T> {
    const response = await fetch(url, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
    });
    if (response.status === 204 || empty) {
      if (!response.ok) {
        throw new ApiError("Request failed", response.status);
      }
      return undefined as T;
    }
    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      throw new ApiError(
        formatApiError(payload, `Request failed (${response.status})`),
        response.status,
      );
    }
    return payload as T;
  }
}

export function createEntitlementsApi(apiBase?: string): EntitlementsApi {
  return new EntitlementsApi(apiBase ?? import.meta.env.VITE_API_BASE ?? "");
}

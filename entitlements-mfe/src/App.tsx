import { useEffect, useMemo, useState } from "react";

import { ApiError, EntitlementsApi } from "./api";
import type {
  Entitlement,
  EntitlementFilters,
  EntitlementStatus,
  Permission,
} from "./types";

const PERMISSIONS: Permission[] = ["view", "execute"];

type AppProps = {
  apiBase?: string;
};

type FormState = {
  automation_key: string;
  ad_group: string;
  granted_by: string;
  expires_at: string;
  permissions: Permission[];
};

const emptyForm: FormState = {
  automation_key: "",
  ad_group: "",
  granted_by: "",
  expires_at: "",
  permissions: ["view"],
};

function toDatetimeLocal(value: string | null): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoOrNull(value: string): string | null {
  if (!value.trim()) {
    return null;
  }
  return new Date(value).toISOString();
}

function formatWhen(value: string | null): string {
  if (!value) {
    return "—";
  }
  return new Date(value).toLocaleString();
}

export function App({ apiBase }: AppProps) {
  const api = useMemo(() => new EntitlementsApi(apiBase ?? ""), [apiBase]);
  const [items, setItems] = useState<Entitlement[]>([]);
  const [filters, setFilters] = useState<EntitlementFilters>({
    automation_key: "",
    ad_group: "",
    status: "",
  });
  const [form, setForm] = useState<FormState>(emptyForm);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [revokedBy, setRevokedBy] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const selected = items.find((item) => item.id === selectedId) ?? null;

  async function refresh() {
    setBusy(true);
    setError(null);
    try {
      const data = await api.list(filters);
      setItems(data);
      if (selectedId && !data.some((item) => item.id === selectedId)) {
        setSelectedId(null);
      }
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Unable to load entitlements");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, filters.automation_key, filters.ad_group, filters.status]);

  async function run(action: () => Promise<void>, success: string) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
      setNotice(success);
      await refresh();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Request failed");
      setBusy(false);
    }
  }

  function togglePermission(permission: Permission, current: Permission[]): Permission[] {
    if (current.includes(permission)) {
      return current.filter((item) => item !== permission);
    }
    return [...current, permission];
  }

  return (
    <div className="mfe">
      <header className="hero">
        <div>
          <p className="eyebrow">Grant register</p>
          <h1>Entitlements</h1>
          <p className="lede">
            Who was given access to which automation, by whom, and when. This
            microfrontend talks only to the entitlements API.
          </p>
        </div>
        <button type="button" onClick={() => void refresh()} disabled={busy}>
          Refresh
        </button>
      </header>

      {error ? (
        <div className="banner error" role="alert">
          {error}
        </div>
      ) : null}
      {notice ? (
        <div className="banner ok" role="status">
          {notice}
        </div>
      ) : null}

      <section className="panel" aria-labelledby="create-heading">
        <h2 id="create-heading">Create grant</h2>
        <form
          className="grid-form"
          onSubmit={(event) => {
            event.preventDefault();
            if (form.permissions.length === 0) {
              setError("Select at least one permission");
              return;
            }
            void run(async () => {
              await api.create({
                automation_key: form.automation_key.trim(),
                ad_group: form.ad_group.trim(),
                granted_by: form.granted_by.trim(),
                permissions: form.permissions,
                expires_at: toIsoOrNull(form.expires_at),
              });
              setForm(emptyForm);
            }, "Grant created");
          }}
        >
          <label>
            Automation key
            <input
              required
              name="automation_key"
              value={form.automation_key}
              onChange={(event) =>
                setForm((current) => ({ ...current, automation_key: event.target.value }))
              }
            />
          </label>
          <label>
            AD group
            <input
              required
              name="ad_group"
              value={form.ad_group}
              onChange={(event) =>
                setForm((current) => ({ ...current, ad_group: event.target.value }))
              }
            />
          </label>
          <label>
            Granted by
            <input
              required
              name="granted_by"
              value={form.granted_by}
              onChange={(event) =>
                setForm((current) => ({ ...current, granted_by: event.target.value }))
              }
            />
          </label>
          <label>
            Expires
            <input
              type="datetime-local"
              name="expires_at"
              value={form.expires_at}
              onChange={(event) =>
                setForm((current) => ({ ...current, expires_at: event.target.value }))
              }
            />
          </label>
          <fieldset>
            <legend>Permissions</legend>
            {PERMISSIONS.map((permission) => (
              <label key={permission} className="check">
                <input
                  type="checkbox"
                  name="permissions"
                  value={permission}
                  checked={form.permissions.includes(permission)}
                  onChange={() =>
                    setForm((current) => ({
                      ...current,
                      permissions: togglePermission(permission, current.permissions),
                    }))
                  }
                />
                {permission}
              </label>
            ))}
          </fieldset>
          <button type="submit" disabled={busy}>
            Create entitlement
          </button>
        </form>
      </section>

      <section className="panel" aria-labelledby="list-heading">
        <div className="panel-head">
          <h2 id="list-heading">Current grants</h2>
          <form
            className="filters"
            onSubmit={(event) => {
              event.preventDefault();
              void refresh();
            }}
          >
            <input
              placeholder="Filter automation key"
              aria-label="Filter automation key"
              value={filters.automation_key ?? ""}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  automation_key: event.target.value,
                }))
              }
            />
            <input
              placeholder="Filter AD group"
              aria-label="Filter AD group"
              value={filters.ad_group ?? ""}
              onChange={(event) =>
                setFilters((current) => ({ ...current, ad_group: event.target.value }))
              }
            />
            <select
              aria-label="Filter status"
              value={filters.status ?? ""}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  status: event.target.value as EntitlementStatus | "",
                }))
              }
            >
              <option value="">All statuses</option>
              <option value="active">active</option>
              <option value="revoked">revoked</option>
            </select>
          </form>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Automation</th>
                <th>AD group</th>
                <th>Permissions</th>
                <th>Granted by</th>
                <th>Granted at</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="empty">
                    {busy ? "Loading entitlements…" : "No entitlements yet."}
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr
                    key={item.id}
                    className={item.id === selectedId ? "selected" : undefined}
                    onClick={() => setSelectedId(item.id)}
                  >
                    <td>{item.automation_key}</td>
                    <td>{item.ad_group}</td>
                    <td>{item.permissions.join(", ")}</td>
                    <td>{item.granted_by}</td>
                    <td>{formatWhen(item.granted_at)}</td>
                    <td>
                      <span className={`status ${item.status}`}>{item.status}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {selected ? (
        <section className="panel" aria-labelledby="detail-heading">
          <h2 id="detail-heading">Manage grant</h2>
          <dl className="meta">
            <div>
              <dt>ID</dt>
              <dd>{selected.id}</dd>
            </div>
            <div>
              <dt>Expires</dt>
              <dd>{formatWhen(selected.expires_at)}</dd>
            </div>
            <div>
              <dt>Revoked by</dt>
              <dd>{selected.revoked_by ?? "—"}</dd>
            </div>
            <div>
              <dt>Revoked at</dt>
              <dd>{formatWhen(selected.revoked_at)}</dd>
            </div>
          </dl>
          <div className="actions">
            <label className="check">
              <input
                type="checkbox"
                checked={selected.permissions.includes("view")}
                onChange={() => {
                  const next = togglePermission("view", selected.permissions);
                  if (next.length === 0) {
                    setError("Select at least one permission");
                    return;
                  }
                  void run(
                    () => api.update(selected.id, { permissions: next }),
                    "Permissions updated",
                  );
                }}
              />
              view
            </label>
            <label className="check">
              <input
                type="checkbox"
                checked={selected.permissions.includes("execute")}
                onChange={() => {
                  const next = togglePermission("execute", selected.permissions);
                  if (next.length === 0) {
                    setError("Select at least one permission");
                    return;
                  }
                  void run(
                    () => api.update(selected.id, { permissions: next }),
                    "Permissions updated",
                  );
                }}
              />
              execute
            </label>
            <label>
              New expiry
              <input
                type="datetime-local"
                defaultValue={toDatetimeLocal(selected.expires_at)}
                onBlur={(event) => {
                  const next = toIsoOrNull(event.target.value);
                  if (next === selected.expires_at) {
                    return;
                  }
                  void run(
                    () => api.update(selected.id, { expires_at: next }),
                    "Expiry updated",
                  );
                }}
              />
            </label>
            {selected.status === "active" ? (
              <>
                <label>
                  Revoked by
                  <input
                    value={revokedBy}
                    onChange={(event) => setRevokedBy(event.target.value)}
                    placeholder="operator id"
                  />
                </label>
                <button
                  type="button"
                  className="danger"
                  disabled={busy}
                  onClick={() => {
                    if (!revokedBy.trim()) {
                      setError("revoked_by is required to revoke a grant");
                      return;
                    }
                    void run(async () => {
                      await api.update(selected.id, {
                        status: "revoked",
                        revoked_by: revokedBy.trim(),
                      });
                      setRevokedBy("");
                    }, "Grant revoked");
                  }}
                >
                  Revoke
                </button>
              </>
            ) : (
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  void run(
                    () => api.update(selected.id, { status: "active" }),
                    "Grant restored",
                  )
                }
              >
                Restore
              </button>
            )}
            <button
              type="button"
              className="danger"
              disabled={busy}
              onClick={() => {
                if (!window.confirm("Delete this entitlement permanently?")) {
                  return;
                }
                void run(async () => {
                  await api.delete(selected.id);
                  setSelectedId(null);
                }, "Grant deleted");
              }}
            >
              Delete
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}

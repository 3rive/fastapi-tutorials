export type Permission = "view" | "execute";
export type EntitlementStatus = "active" | "revoked";

export type Entitlement = {
  id: string;
  automation_key: string;
  ad_group: string;
  permissions: Permission[];
  granted_by: string;
  granted_at: string;
  expires_at: string | null;
  status: EntitlementStatus;
  revoked_by: string | null;
  revoked_at: string | null;
  schema_version: number;
};

export type EntitlementCreate = {
  automation_key: string;
  ad_group: string;
  permissions: Permission[];
  granted_by: string;
  expires_at?: string | null;
};

export type EntitlementUpdate = {
  permissions?: Permission[];
  expires_at?: string | null;
  status?: EntitlementStatus;
  revoked_by?: string;
};

export type EntitlementFilters = {
  automation_key?: string;
  ad_group?: string;
  status?: EntitlementStatus | "";
};

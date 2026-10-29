// Thin fetch wrapper. The Next.js server proxies /api/* to the FastAPI backend (see next.config.js).
export type Session = { token: string; user: { user_id: string; name: string; email: string; role: string; department_id?: string } };

const KEY = "hqb.session";

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  try { return JSON.parse(sessionStorage.getItem(KEY) || "null"); } catch { return null; }
}
export function setSession(s: Session) { sessionStorage.setItem(KEY, JSON.stringify(s)); }
export function clearSession() { sessionStorage.removeItem(KEY); }

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}

export async function api<T = any>(path: string, opts: { method?: string; body?: any; form?: FormData } = {}): Promise<T> {
  const s = getSession();
  const headers: Record<string, string> = {};
  if (s) headers.Authorization = `Bearer ${s.token}`;
  let body: BodyInit | undefined;
  if (opts.form) body = opts.form;
  else if (opts.body !== undefined) { headers["Content-Type"] = "application/json"; body = JSON.stringify(opts.body); }
  let res: Response;
  try {
    res = await fetch(`/api${path}`, { method: opts.method || (body ? "POST" : "GET"), headers, body });
  } catch {
    throw new ApiError(0, "Cannot reach the server. Check that the backend is running.");
  }
  if (res.status === 401 && !path.startsWith("/auth/login")) {
    clearSession();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new ApiError(401, "Your session has expired. Please sign in again.");
  }
  const text = await res.text();
  let data: any = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const d = data && data.detail;
    const msg = typeof d === "string" ? d : Array.isArray(d) ? d.map((x: any) => x.msg).join("; ") : `Request failed (${res.status})`;
    throw new ApiError(res.status, msg);
  }
  return data as T;
}

export async function downloadDocument(id: string, name: string) {
  const s = getSession();
  const res = await fetch(`/api/documents/${id}/download`, { headers: { Authorization: `Bearer ${s?.token}` } });
  if (!res.ok) throw new ApiError(res.status, "Could not download the document");
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  URL.revokeObjectURL(url);
}

export const fmtDate = (iso?: string) => iso ? new Date(iso).toLocaleString(undefined, { day: "numeric", month: "short", year: "numeric", hour: "numeric", minute: "2-digit" }) : "";
export const fmtDay = (iso?: string) => iso ? new Date(iso + (iso.length === 10 ? "T00:00:00" : "")).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" }) : "";
export const clean = (e: any) => (e instanceof Error ? e.message : String(e)).replace(/^(Validation Failed|Security Error|State Error|Database Error|System Error|Concurrency Error|API Error|Cloud Error|Resolution Error|Authentication Failed): ?/, "");

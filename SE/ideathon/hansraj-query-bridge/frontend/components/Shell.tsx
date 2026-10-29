"use client";
import { ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { api, clearSession, fmtDate, getSession } from "@/lib/api";

type Tab = { id: string; label: string };

function Bell({ onOpenQuery }: { onOpenQuery?: (id: string) => void }) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<{ unread: number; items: any[] }>({ unread: 0, items: [] });
  const ref = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try { setData(await api("/notifications")); } catch { /* transient */ }
  }, []);
  useEffect(() => { load(); const t = setInterval(load, 25000); return () => clearInterval(t); }, [load]);
  useEffect(() => {
    const close = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", close); document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", close); document.removeEventListener("keydown", esc); };
  }, []);

  async function readAll() { await api("/notifications/read-all", { method: "POST" }); load(); }
  async function openItem(n: any) {
    if (!n.is_read) await api(`/notifications/${n.notification_id}/read`, { method: "POST" });
    if (n.related_query_id && onOpenQuery) { onOpenQuery(n.related_query_id); setOpen(false); }
    load();
  }

  return (
    <div className="bell" ref={ref}>
      <button className="btn sm" aria-haspopup="true" aria-expanded={open} onClick={() => { setOpen(!open); if (!open) load(); }}>
        Notifications
        {data.unread > 0 && <span className="count" aria-label={`${data.unread} unread`}>{data.unread}</span>}
      </button>
      {open && (
        <div className="panel" role="dialog" aria-label="Notifications">
          <div className="head"><b>Notifications</b>{data.unread > 0 && <button className="btn ghost sm" onClick={readAll}>Mark all read</button>}</div>
          {data.items.length === 0 && <div className="empty"><b>Nothing yet</b>Updates on your queries will show up here.</div>}
          {data.items.map((n) => (
            <div key={n.notification_id} className={`notif ${n.is_read ? "" : "unread"}`}>
              <div>{n.message}</div>
              <time>{fmtDate(n.created_at)}</time>
              {n.related_query_id && onOpenQuery && <button className="btn ghost sm" style={{ marginTop: 6 }} onClick={() => openItem(n)}>Open query</button>}
              {!(n.related_query_id && onOpenQuery) && !n.is_read && <button className="btn ghost sm" style={{ marginTop: 6 }} onClick={() => openItem(n)}>Mark read</button>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Shell({ role, tabs, tab, onTab, onOpenQuery, children }: {
  role: "Student" | "Admin" | "TIC"; tabs: Tab[]; tab: string; onTab: (t: string) => void; onOpenQuery?: (id: string) => void; children: ReactNode;
}) {
  const [ready, setReady] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    const s = getSession();
    if (!s) { window.location.replace("/login"); return; }
    if (s.user.role !== role) { window.location.replace(`/${s.user.role.toLowerCase()}/dashboard`); return; }
    setName(s.user.name); setReady(true);
  }, [role]);

  async function logout() {
    try { await api("/auth/logout", { method: "POST" }); } catch { /* already invalid */ }
    clearSession(); window.location.replace("/login");
  }
  if (!ready) return null;
  const roleLabel = role === "TIC" ? "Teacher-in-Charge" : role;
  return (
    <>
      <header className="topbar">
        <div className="in">
          <div className="wordmark">Hansraj Query Bridge<small>{roleLabel} workspace</small></div>
          <div className="grow" />
          <div className="who"><b>{name}</b>{roleLabel}</div>
          <Bell onOpenQuery={onOpenQuery} />
          <button className="btn sm" onClick={logout}>Sign out</button>
        </div>
      </header>
      <nav className="tabs" aria-label="Sections">
        <div className="in" role="tablist">
          {tabs.map((t) => <button key={t.id} role="tab" className="tab" aria-selected={tab === t.id} onClick={() => onTab(t.id)}>{t.label}</button>)}
        </div>
      </nav>
      <main className="page">{children}</main>
    </>
  );
}

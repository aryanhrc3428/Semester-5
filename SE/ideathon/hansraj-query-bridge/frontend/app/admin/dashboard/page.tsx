"use client";
import { useCallback, useEffect, useState } from "react";
import Shell from "@/components/Shell";
import QueryDetail, { QueryList } from "@/components/QueryDetail";
import KbManager from "@/components/KbManager";
import { Empty, useToast } from "@/components/ui";
import { api, clean, fmtDate } from "@/lib/api";

function QueueTab({ mode }: { mode: "new" | "all" }) {
  const toast = useToast();
  const [items, setItems] = useState<any[] | null>(null);
  const [sel, setSel] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [q, setQ] = useState("");
  const load = useCallback(async () => {
    try {
      if (mode === "new") setItems((await api("/admin/queries/new")).data);
      else setItems(await api(`/admin/queries?${status ? `status=${encodeURIComponent(status)}&` : ""}${q ? `q=${encodeURIComponent(q)}` : ""}`));
    } catch (e) { toast(clean(e), true); setItems([]); }
  }, [mode, status, q, toast]);
  useEffect(() => { const t = setTimeout(load, 200); return () => clearTimeout(t); }, [load]);
  useEffect(() => { setSel(null); }, [mode]);
  return (
    <div className="split">
      <div>
        <h2 style={{ marginBottom: 12 }}>{mode === "new" ? "New queries" : "All queries"}</h2>
        {mode === "all" && (
          <div className="row" style={{ marginBottom: 12 }}>
            <input type="text" aria-label="Search queries" className="grow" placeholder="Search…" value={q} onChange={(e) => setQ(e.target.value)} style={{ flex: 1 }} />
            <select aria-label="Status filter" value={status} onChange={(e) => setStatus(e.target.value)} style={{ width: "auto" }}>
              <option value="">All statuses</option>{["Open", "Assigned to TIC", "Documents Required", "Document Submitted", "Resolved"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
        )}
        {items === null ? <div className="card muted">Loading…</div> : <QueryList items={items} selected={sel} onSelect={setSel} showStudent empty={mode === "new" ? "No new queries. You’re all caught up." : "No queries match"} />}
      </div>
      <div>{sel ? <QueryDetail id={sel} role="Admin" onChanged={load} /> : <div className="card"><Empty title="Select a query">Resolve it, or forward it to the right teacher.</Empty></div>}</div>
    </div>
  );
}

function Audit() {
  const [rows, setRows] = useState<any[] | null>(null);
  const [action, setAction] = useState("");
  useEffect(() => { const t = setTimeout(() => api(`/admin/audit?limit=200${action ? `&action=${encodeURIComponent(action)}` : ""}`).then(setRows).catch(() => setRows([])), 250); return () => clearTimeout(t); }, [action]);
  return (
    <div>
      <div className="row" style={{ marginBottom: 12 }}>
        <h2 className="grow">Audit log</h2>
        <input type="text" aria-label="Filter by action" placeholder="Filter by action (e.g. Resolve)" value={action} onChange={(e) => setAction(e.target.value)} style={{ maxWidth: 280 }} />
      </div>
      <div className="card flush tablewrap">
        {rows === null ? <p className="muted" style={{ padding: 16 }}>Loading…</p> : (
          <table>
            <thead><tr><th>When</th><th>Who</th><th>Action</th><th>Entity</th><th>Reference</th></tr></thead>
            <tbody>{rows.map((r) => <tr key={r.audit_id}><td>{fmtDate(r.timestamp)}</td><td>{r.user_name}</td><td>{r.action_type}</td><td>{r.entity}</td><td style={{ fontFamily: "monospace", fontSize: 12 }}>{r.entity_id?.slice(0, 8)}</td></tr>)}</tbody>
          </table>
        )}
      </div>
      <p className="hint" style={{ marginTop: 8 }}>The audit log is append-only; records cannot be edited or deleted.</p>
    </div>
  );
}

export default function AdminDashboard() {
  const [tab, setTab] = useState("new");
  const [stats, setStats] = useState<any>(null);
  useEffect(() => { api("/admin/stats").then(setStats).catch(() => {}); }, [tab]);
  const s = stats?.by_status || {};
  const tabs = [{ id: "new", label: `New queries${s.Open ? ` (${s.Open})` : ""}` }, { id: "all", label: "All queries" }, { id: "kb", label: "Knowledge base" }, { id: "audit", label: "Audit log" }];
  return (
    <Shell role="Admin" tabs={tabs} tab={tab} onTab={setTab}>
      {stats && (
        <div className="stats">
          <div className="stat"><b>{s.Open || 0}</b><span>Waiting for triage</span></div>
          <div className="stat"><b>{(s["Assigned to TIC"] || 0) + (s["Documents Required"] || 0) + (s["Document Submitted"] || 0)}</b><span>With teachers</span></div>
          <div className="stat"><b>{s.Resolved || 0}</b><span>Resolved</span></div>
          <div className="stat"><b>{stats.ai?.answered || 0}<small style={{ fontSize: 14 }}> / {(stats.ai?.answered || 0) + (stats.ai?.escalate || 0)}</small></b><span>Questions the assistant answered</span></div>
          <div className="stat"><b>{stats.active_kb_entries}</b><span>Active knowledge entries</span></div>
        </div>
      )}
      {tab === "new" && <QueueTab mode="new" />}
      {tab === "all" && <QueueTab mode="all" />}
      {tab === "kb" && <div><h2 style={{ marginBottom: 12 }}>Knowledge base</h2><KbManager /></div>}
      {tab === "audit" && <Audit />}
    </Shell>
  );
}

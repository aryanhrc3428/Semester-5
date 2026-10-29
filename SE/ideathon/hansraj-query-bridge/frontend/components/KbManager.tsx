"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, clean, fmtDate } from "@/lib/api";
import { Empty, StatusBadge, useToast } from "./ui";

const CATS = ["Academic", "Administrative", "Technical", "Financial"];
const blank = { title: "", content: "", category: "Administrative", source: "" };

export default function KbManager() {
  const toast = useToast();
  const [items, setItems] = useState<any[] | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("Active");
  const [form, setForm] = useState<any>(null);   // null = hidden, {kb_id?} = editing
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try { setItems(await api(`/kb?status=${status}${q ? `&q=${encodeURIComponent(q)}` : ""}`)); }
    catch (e) { toast(clean(e), true); setItems([]); }
  }, [q, status, toast]);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);

  async function save(e: FormEvent) {
    e.preventDefault(); setBusy(true);
    try {
      if (form.kb_id) await api(`/kb/${form.kb_id}`, { method: "PUT", body: { title: form.title, content: form.content, category: form.category, source: form.source || null } });
      else await api("/kb", { body: { title: form.title, content: form.content, category: form.category, source: form.source || null } });
      toast(form.kb_id ? "Entry updated." : "Entry added. The assistant can use it right away.");
      setForm(null); load();
    } catch (err) { toast(clean(err), true); } finally { setBusy(false); }
  }
  async function act(id: string, what: "deactivate" | "archive") {
    try { await api(`/kb/${id}/${what}`, { method: "POST" }); toast(what === "archive" ? "Entry archived." : "Entry deactivated."); load(); }
    catch (err) { toast(clean(err), true); }
  }

  return (
    <div>
      <div className="row" style={{ marginBottom: 14 }}>
        <div className="field grow" style={{ margin: 0, minWidth: 220 }}>
          <label htmlFor="kbq" className="label">Search</label>
          <input id="kbq" type="text" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search title or answer" />
        </div>
        <div className="field" style={{ margin: 0 }}>
          <label htmlFor="kbs" className="label">Show</label>
          <select id="kbs" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option>Active</option><option>Inactive</option><option>Archived</option>
          </select>
        </div>
        <button className="btn" style={{ alignSelf: "flex-end" }} onClick={() => setForm({ ...blank })}>Add entry</button>
      </div>

      {form && (
        <form onSubmit={save} className="card" style={{ marginBottom: 14 }}>
          <h3>{form.kb_id ? "Edit entry" : "New knowledge base entry"}</h3>
          <div className="field" style={{ marginTop: 10 }}>
            <label htmlFor="kt">Question or title</label>
            <input id="kt" type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required maxLength={300} />
          </div>
          <div className="field">
            <label htmlFor="kc">Verified answer</label>
            <textarea id="kc" style={{ minHeight: 130 }} value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} required />
            <span className="hint">Write the full, verified answer. Students will see it, so keep it accurate and complete.</span>
          </div>
          <div className="row">
            <div className="field grow">
              <label htmlFor="kcat">Category</label>
              <select id="kcat" value={form.category || ""} onChange={(e) => setForm({ ...form, category: e.target.value })}>{CATS.map((c) => <option key={c}>{c}</option>)}</select>
            </div>
            <div className="field grow">
              <label htmlFor="ksrc">Source</label>
              <input id="ksrc" type="text" value={form.source || ""} onChange={(e) => setForm({ ...form, source: e.target.value })} placeholder="e.g. College prospectus 2026" />
            </div>
          </div>
          <div className="row">
            <button className="btn" disabled={busy}>{busy ? "Saving…" : "Save entry"}</button>
            <button type="button" className="btn ghost" onClick={() => setForm(null)}>Cancel</button>
          </div>
        </form>
      )}

      {items === null ? <div className="card muted">Loading…</div> : items.length === 0 ? <div className="card"><Empty title="No entries here">Add verified answers so the assistant can respond to students.</Empty></div> : (
        items.map((k) => (
          <div className="card" key={k.kb_id}>
            <div className="row">
              <h3 className="grow">{k.title}</h3><StatusBadge status={k.validity_status} />
            </div>
            <p style={{ marginTop: 8, whiteSpace: "pre-wrap" }}>{k.content}</p>
            <p className="muted small">{k.category} · v{k.version} · {k.source || "No source"} · updated {fmtDate(k.updated_at)}</p>
            {k.validity_status === "Active" && (
              <div className="row" style={{ marginTop: 8 }}>
                <button className="btn sm ghost" onClick={() => setForm({ kb_id: k.kb_id, title: k.title, content: k.content, category: k.category || "Administrative", source: k.source || "" })}>Edit</button>
                <button className="btn sm ghost" onClick={() => act(k.kb_id, "deactivate")}>Deactivate</button>
                <button className="btn sm ghost" onClick={() => act(k.kb_id, "archive")}>Archive</button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

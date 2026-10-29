"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, clean, downloadDocument, fmtDate, fmtDay } from "@/lib/api";
import { Empty, Progress, StatusBadge, useToast } from "./ui";

type Role = "Student" | "Admin" | "TIC";
const MAX = 25 * 1024 * 1024;
const today = () => new Date().toISOString().slice(0, 10);

function Resolve({ role, id, onDone }: { role: Role; id: string; onDone: () => void }) {
  const toast = useToast();
  const [text, setText] = useState("");
  const [kb, setKb] = useState(false);
  const [busy, setBusy] = useState(false);
  const base = role === "Admin" ? "/admin/queries" : "/tic/queries";
  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true);
    try {
      await api(`${base}/${id}/resolve`, { body: { resolution: text, add_to_kb: kb } });
      toast("Query resolved. The student has been notified.");
      setText(""); setKb(false); onDone();
    } catch (err) { toast(clean(err), true); } finally { setBusy(false); }
  }
  return (
    <form onSubmit={submit} className="card">
      <h3>Resolve this query</h3>
      <div className="field" style={{ marginTop: 10 }}>
        <label htmlFor={`res-${id}`}>Resolution for the student</label>
        <textarea id={`res-${id}`} value={text} onChange={(e) => setText(e.target.value)} minLength={10} maxLength={5000} required />
        <span className="hint">{text.length}/5000 · at least 10 characters</span>
      </div>
      <label className="check" style={{ marginBottom: 12 }}>
        <input type="checkbox" checked={kb} onChange={(e) => setKb(e.target.checked)} />
        <span>Add this answer to the knowledge base so the assistant can answer similar questions</span>
      </label>
      <button className="btn" disabled={busy || text.trim().length < 10}>{busy ? "Resolving…" : "Mark as resolved"}</button>
    </form>
  );
}

function Forward({ id, onDone }: { id: string; onDone: () => void }) {
  const toast = useToast();
  const [tics, setTics] = useState<any[]>([]);
  const [sel, setSel] = useState("");
  useEffect(() => {
    api(`/admin/queries/${id}/tic-suggestions`).then((r) => { setTics(r); const s = r.find((t: any) => t.suggested); if (s) setSel(s.user_id); }).catch(() => {});
  }, [id]);
  async function go(e: FormEvent) {
    e.preventDefault();
    try { await api(`/admin/queries/${id}/forward`, { body: { tic_id: sel } }); toast("Forwarded to the teacher."); onDone(); }
    catch (err) { toast(clean(err), true); }
  }
  return (
    <form onSubmit={go} className="card">
      <h3>Forward to a teacher-in-charge</h3>
      <div className="field" style={{ marginTop: 10 }}>
        <label htmlFor={`tic-${id}`}>Teacher</label>
        <select id={`tic-${id}`} value={sel} onChange={(e) => setSel(e.target.value)} required>
          <option value="" disabled>Select a teacher</option>
          {tics.map((t) => <option key={t.user_id} value={t.user_id}>{t.name} · {t.department_name} · {t.open_queries} open{t.suggested ? " · suggested" : ""}</option>)}
        </select>
        <span className="hint">Suggested: same department with the lightest workload.</span>
      </div>
      <button className="btn" disabled={!sel}>Forward query</button>
    </form>
  );
}

function RequestDoc({ id, onDone }: { id: string; onDone: () => void }) {
  const toast = useToast();
  const [note, setNote] = useState("");
  async function go(e: FormEvent) {
    e.preventDefault();
    try { await api(`/tic/queries/${id}/request-document`, { body: { note } }); toast("Document requested. The student has been notified."); setNote(""); onDone(); }
    catch (err) { toast(clean(err), true); }
  }
  return (
    <form onSubmit={go} className="card">
      <h3>Request a document</h3>
      <div className="field" style={{ marginTop: 10 }}>
        <label htmlFor={`dn-${id}`}>What should the student upload?</label>
        <textarea id={`dn-${id}`} style={{ minHeight: 70 }} value={note} onChange={(e) => setNote(e.target.value)} minLength={5} maxLength={1000} required />
      </div>
      <button className="btn ghost" disabled={note.trim().length < 5}>Send request</button>
    </form>
  );
}

function ReviewControls({ qid, doc, onDone }: { qid: string; doc: any; onDone: () => void }) {
  const toast = useToast();
  const [rejecting, setRejecting] = useState(false);
  const [notes, setNotes] = useState("");
  async function review(decision: string) {
    try { await api(`/tic/queries/${qid}/documents/${doc.document_id}/review`, { body: { decision, notes: decision === "Reject" ? notes : null } }); toast(`Document ${decision === "Accept" ? "accepted" : "rejected"}.`); onDone(); }
    catch (err) { toast(clean(err), true); }
  }
  if (!rejecting) return (
    <div className="row" style={{ marginTop: 8 }}>
      <button className="btn sm" onClick={() => review("Accept")}>Accept</button>
      <button className="btn sm ghost" onClick={() => setRejecting(true)}>Reject…</button>
    </div>
  );
  return (
    <div style={{ marginTop: 8 }}>
      <label className="label" htmlFor={`rj-${doc.document_id}`}>Why is it being rejected?</label>
      <textarea id={`rj-${doc.document_id}`} style={{ minHeight: 64 }} value={notes} onChange={(e) => setNotes(e.target.value)} />
      <div className="row" style={{ marginTop: 8 }}>
        <button className="btn sm danger" disabled={notes.trim().length < 5} onClick={() => review("Reject")}>Reject document</button>
        <button className="btn sm ghost" onClick={() => setRejecting(false)}>Cancel</button>
      </div>
    </div>
  );
}

function Upload({ id, onDone }: { id: string; onDone: () => void }) {
  const toast = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  function pick(f: File | null) {
    if (f) {
      const ext = f.name.split(".").pop()?.toLowerCase();
      if (!["pdf", "jpg", "jpeg", "png"].includes(ext || "")) { toast("Only PDF, JPG, JPEG or PNG files are accepted.", true); return; }
      if (f.size === 0 || f.size > MAX) { toast("The file must be between 1 byte and 25 MB.", true); return; }
    }
    setFile(f);
  }
  async function go(e: FormEvent) {
    e.preventDefault(); if (!file) return; setBusy(true);
    const form = new FormData(); form.append("file", file);
    try { await api(`/student/queries/${id}/documents`, { form }); toast("Document uploaded. Your teacher will review it."); setFile(null); onDone(); }
    catch (err) { toast(clean(err), true); } finally { setBusy(false); }
  }
  return (
    <form onSubmit={go} className="row" style={{ marginTop: 10 }}>
      <label className="sr-only" htmlFor={`up-${id}`} style={{ position: "absolute", left: -9999 }}>Choose a document</label>
      <input id={`up-${id}`} type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => pick(e.target.files?.[0] || null)} />
      <button className="btn sm" disabled={!file || busy}>{busy ? "Uploading…" : "Upload document"}</button>
    </form>
  );
}

function BookMeeting({ id, onDone }: { id: string; onDone: () => void }) {
  const toast = useToast();
  const [date, setDate] = useState(today());
  const [slots, setSlots] = useState<any[] | null>(null);
  const [tic, setTic] = useState("");
  useEffect(() => {
    setSlots(null);
    api(`/student/queries/${id}/slots?date=${date}`).then((r) => { setSlots(r.slots); setTic(r.tic_name); }).catch(() => setSlots([]));
  }, [id, date]);
  async function request(slot_id: string) {
    try { await api("/student/slots/request", { body: { slot_id, query_id: id } }); toast("Meeting requested. You’ll be notified when it’s accepted."); onDone(); setDate(date); }
    catch (err) { toast(clean(err), true); }
  }
  return (
    <div className="card">
      <h3>Request a meeting{tic ? ` with ${tic}` : ""}</h3>
      <div className="field" style={{ marginTop: 10, maxWidth: 220 }}>
        <label htmlFor={`md-${id}`}>Date</label>
        <input id={`md-${id}`} type="date" min={today()} value={date} onChange={(e) => setDate(e.target.value)} />
      </div>
      {slots === null ? <p className="muted">Loading slots…</p> : slots.length === 0 ? <p className="muted small">No open slots on this date. Try another day.</p> : (
        <div className="chips">{slots.map((s) => <button key={s.slot_id} className="chip" onClick={() => request(s.slot_id)}>{s.start_time}–{s.end_time}</button>)}</div>
      )}
    </div>
  );
}

function ScheduleMeeting({ id, onDone }: { id: string; onDone: () => void }) {
  const toast = useToast();
  const [date, setDate] = useState(today());
  const [free, setFree] = useState<any[] | null>(null);
  useEffect(() => {
    setFree(null);
    api(`/tic/timetable?date=${date}`).then((r) => setFree(r.data)).catch(() => setFree([]));
  }, [date]);
  async function schedule(p: any) {
    try { await api("/tic/meetings", { body: { query_id: id, date, start_time: p.start_time, end_time: p.end_time } }); toast("Meeting scheduled. The student has been notified."); onDone(); setDate(date); }
    catch (err) { toast(clean(err), true); }
  }
  return (
    <div className="card">
      <h3>Schedule a meeting</h3>
      <div className="field" style={{ marginTop: 10, maxWidth: 220 }}>
        <label htmlFor={`sm-${id}`}>Date</label>
        <input id={`sm-${id}`} type="date" min={today()} value={date} onChange={(e) => setDate(e.target.value)} />
      </div>
      {free === null ? <p className="muted">Checking your timetable…</p> : free.length === 0 ? <p className="muted small">No free periods on this date.</p> : (
        <div className="chips">{free.map((p) => <button key={p.start_time} className="chip" onClick={() => schedule(p)}>{p.start_time}–{p.end_time}</button>)}</div>
      )}
    </div>
  );
}

export default function QueryDetail({ id, role, onChanged }: { id: string; role: Role; onChanged?: () => void }) {
  const [d, setD] = useState<any>(null);
  const [err, setErr] = useState("");
  const load = useCallback(async () => {
    try { setD(await api(`/queries/${id}`)); setErr(""); } catch (e) { setErr(clean(e)); }
  }, [id]);
  useEffect(() => { setD(null); load(); }, [load]);
  const changed = () => { load(); onChanged?.(); };

  if (err) return <div className="alert bad" role="alert">{err}</div>;
  if (!d) return <div className="card muted">Loading…</div>;
  const q = d.query;
  const open = q.status !== "Resolved";
  const download = (doc: any) => downloadDocument(doc.document_id, doc.file_name).catch(() => {});

  return (
    <div>
      <div className="card">
        <div className="row" style={{ marginBottom: 8 }}>
          <StatusBadge status={q.status} /><span className="badge b-neutral">{q.category}</span>
          {q.department_name && <span className="muted small">{q.department_name}</span>}
        </div>
        <h2 style={{ fontSize: 18, whiteSpace: "pre-wrap" }}>{q.description}</h2>
        <p className="muted small" style={{ marginTop: 8 }}>
          {role !== "Student" && <>From <b>{q.student_name}</b> · </>}Raised {fmtDate(q.created_at)}
          {q.tic_name && <> · Teacher: {q.tic_name}</>}
        </p>
        <Progress status={q.status} />
        {q.status === "Resolved" && q.resolution && (
          <div className="alert ok" style={{ marginTop: 12, marginBottom: 0, whiteSpace: "pre-wrap" }}><b>Resolution</b><br />{q.resolution}</div>
        )}
        {q.status === "Documents Required" && q.doc_request_note && (
          <div className="alert info" style={{ marginTop: 12, marginBottom: 0 }}><b>Document requested</b><br />{q.doc_request_note}</div>
        )}
      </div>

      {(d.documents.length > 0 || (role === "Student" && q.status === "Documents Required")) && (
        <div className="card">
          <h3>Documents</h3>
          {d.documents.map((doc: any) => (
            <div key={doc.document_id} style={{ padding: "10px 0", borderBottom: "1px solid var(--line)" }}>
              <div className="row">
                <span className="grow" style={{ wordBreak: "break-all" }}>{doc.file_name}</span>
                <StatusBadge status={doc.status} />
                <button className="btn ghost sm" onClick={() => download(doc)}>Download</button>
              </div>
              {doc.review_notes && <p className="small muted" style={{ marginTop: 4 }}>Reviewer note: {doc.review_notes}</p>}
              {role === "TIC" && doc.status === "Pending Review" && <ReviewControls qid={id} doc={doc} onDone={changed} />}
            </div>
          ))}
          {role === "Student" && q.status === "Documents Required" && <Upload id={id} onDone={changed} />}
        </div>
      )}

      {d.meetings.length > 0 && (
        <div className="card">
          <h3>Meetings</h3>
          {d.meetings.map((m: any) => (
            <div key={m.meeting_id} className="row" style={{ padding: "8px 0" }}>
              <span className="grow">{fmtDay(m.date)} · {m.start_time}–{m.end_time} · {m.tic_name}</span><StatusBadge status={m.status} />
            </div>
          ))}
        </div>
      )}

      {role === "Student" && open && q.assigned_tic && <BookMeeting id={id} onDone={changed} />}
      {role === "Admin" && open && q.status === "Open" && <Forward id={id} onDone={changed} />}
      {role === "Admin" && open && <Resolve role="Admin" id={id} onDone={changed} />}
      {role === "TIC" && open && <RequestDoc id={id} onDone={changed} />}
      {role === "TIC" && open && <ScheduleMeeting id={id} onDone={changed} />}
      {role === "TIC" && open && <Resolve role="TIC" id={id} onDone={changed} />}

      <div className="card">
        <h3>History</h3>
        {d.timeline.length === 0 ? <p className="muted small">No activity yet.</p> : (
          <ul className="timeline">
            {d.timeline.map((t: any, i: number) => <li key={i}>{t.action_type}{t.by_name ? ` · ${t.by_name}` : ""}<time>{fmtDate(t.timestamp)}</time></li>)}
          </ul>
        )}
      </div>
    </div>
  );
}

export function QueryList({ items, selected, onSelect, showStudent, empty }: {
  items: any[]; selected: string | null; onSelect: (id: string) => void; showStudent?: boolean; empty: string;
}) {
  if (!items.length) return <div className="card"><Empty title={empty} /></div>;
  return (
    <div className="card flush">
      <ul className="list">
        {items.map((it) => {
          const q = it.query_details || it;
          const who = it.student_info?.name || q.student_name;
          return (
            <li key={q.query_id}>
              <button aria-current={selected === q.query_id} onClick={() => onSelect(q.query_id)}>
                <div className="t">{q.description}</div>
                <div className="m"><StatusBadge status={q.status} /><span>{q.category}</span>{showStudent && who && <span>· {who}</span>}<span>· {fmtDate(q.updated_at)}</span></div>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

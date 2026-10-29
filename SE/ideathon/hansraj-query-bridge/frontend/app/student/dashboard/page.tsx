"use client";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import Shell from "@/components/Shell";
import QueryDetail, { QueryList } from "@/components/QueryDetail";
import { Empty, StatusBadge, useToast } from "@/components/ui";
import { api, clean, fmtDay } from "@/lib/api";

const CATS = ["Academic", "Administrative", "Technical", "Financial"];
const EXAMPLES = ["How do I get a bonafide certificate?", "How do I apply for re-evaluation?", "What if I lose my ID card?"];

type Msg = { id: number; from: "me" | "bot"; text: string; sources?: any[]; escalate?: { question: string; dept?: string | null }; };

function RaiseForm({ initial, dept, fromAi, depts, onDone, onCancel }: any) {
  const toast = useToast();
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState(initial || "");
  const [department, setDepartment] = useState(dept || "");
  const [category, setCategory] = useState("Academic");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!department && desc.trim().length > 15) {
      const t = setTimeout(() => api("/student/suggest-department", { body: { query: desc } }).then((r) => { if (r.department_id) setDepartment((d: string) => d || r.department_id); }).catch(() => {}), 500);
      return () => clearTimeout(t);
    }
  }, [desc, department]);
  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true);
    try {
      const r = await api("/student/queries", { body: { title: title || null, description: desc, department_id: department, category, from_ai: !!fromAi } });
      toast("Your query was sent to the college staff.");
      onDone(r.data.query_id);
    } catch (err) { toast(clean(err), true); } finally { setBusy(false); }
  }
  return (
    <form className="card" onSubmit={submit} style={{ maxWidth: 720 }}>
      <h2 style={{ marginBottom: 12 }}>Send a query to the college</h2>
      <div className="field">
        <label htmlFor="rt">Subject (optional)</label>
        <input id="rt" type="text" value={title} maxLength={150} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="rd">Describe your query</label>
        <textarea id="rd" value={desc} onChange={(e) => setDesc(e.target.value)} minLength={10} maxLength={2000} required />
        <span className="hint">{desc.length}/2000 · at least 10 characters. Include the course, semester or document name if relevant.</span>
      </div>
      <div className="row">
        <div className="field grow">
          <label htmlFor="rdep">Department</label>
          <select id="rdep" value={department} onChange={(e) => setDepartment(e.target.value)} required>
            <option value="" disabled>Select a department</option>
            {depts.map((d: any) => <option key={d.dept_id} value={d.dept_id}>{d.department_name}</option>)}
          </select>
        </div>
        <div className="field grow">
          <label htmlFor="rcat">Category</label>
          <select id="rcat" value={category} onChange={(e) => setCategory(e.target.value)}>{CATS.map((c) => <option key={c}>{c}</option>)}</select>
        </div>
      </div>
      <div className="row">
        <button className="btn" disabled={busy || desc.trim().length < 10 || !department}>{busy ? "Sending…" : "Send query"}</button>
        <button type="button" className="btn ghost" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

function Ask({ depts, onRaise }: { depts: any[]; onRaise: (q: string, dept?: string | null, fromAi?: boolean) => void }) {
  const toast = useToast();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [msgs, busy]);

  async function send(question: string) {
    const q = question.trim();
    if (q.length < 5 || busy) return;
    setText(""); setBusy(true);
    setMsgs((m) => [...m, { id: Date.now(), from: "me", text: q }]);
    try {
      const r = await api("/student/ask", { body: { query: q } });
      if (r.status === "answered") setMsgs((m) => [...m, { id: Date.now() + 1, from: "bot", text: r.answer, sources: r.sources }]);
      else if (r.status === "clarify") setMsgs((m) => [...m, { id: Date.now() + 1, from: "bot", text: r.message }]);
      else setMsgs((m) => [...m, { id: Date.now() + 1, from: "bot", text: r.message, escalate: { question: q, dept: r.suggested_department_id } }]);
    } catch (err: any) {
      const unavailable = err.status === 503 || err.status === 0;
      setMsgs((m) => [...m, { id: Date.now() + 1, from: "bot", text: unavailable ? "The assistant is unavailable right now. You can send your question to the college staff instead." : clean(err), escalate: unavailable ? { question: q } : undefined }]);
      if (!unavailable) toast(clean(err), true);
    } finally { setBusy(false); }
  }

  return (
    <div className="ask">
      <h1>What do you need from the college?</h1>
      <p className="muted">Answers come only from information the college has verified. If there isn’t one, you can send the question straight to the right teacher.</p>
      {msgs.length === 0 && (
        <div className="chips" aria-label="Example questions">{EXAMPLES.map((e) => <button key={e} className="chip" onClick={() => send(e)}>{e}</button>)}</div>
      )}
      <div className="thread" aria-live="polite">
        {msgs.map((m) => (
          <div key={m.id} className={`msg ${m.from}`}>
            {m.text}
            {m.sources && m.sources.length > 0 && <div className="src">Verified source: {m.sources.map((s) => s.source || s.title).join(" · ")}</div>}
            {m.escalate && <div className="chips"><button className="btn sm" onClick={() => onRaise(m.escalate!.question, m.escalate!.dept, true)}>Send to college staff</button></div>}
          </div>
        ))}
        {busy && <div className="msg bot typing">Looking through verified answers…</div>}
        <div ref={end} />
      </div>
      <form className="composer" onSubmit={(e) => { e.preventDefault(); send(text); }}>
        <label htmlFor="ask" style={{ position: "absolute", left: -9999 }}>Your question</label>
        <textarea id="ask" value={text} rows={2} maxLength={1000} placeholder="Type your question…" onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(text); } }} />
        <button className="btn" disabled={busy || text.trim().length < 5}>Ask</button>
      </form>
      <p className="hint" style={{ marginTop: 8 }}>Can’t find what you need? <a href="#" onClick={(e) => { e.preventDefault(); onRaise("", null, false); }}>Send a query directly</a>.</p>
    </div>
  );
}

function Meetings() {
  const [d, setD] = useState<any>(null);
  useEffect(() => { api("/student/meetings").then(setD).catch(() => setD({ meetings: [], pending_requests: [] })); }, []);
  if (!d) return <div className="card muted">Loading…</div>;
  return (
    <div style={{ maxWidth: 720 }}>
      <h2 style={{ marginBottom: 12 }}>Your meetings</h2>
      {d.pending_requests.length > 0 && (
        <div className="card"><h3>Waiting for the teacher to accept</h3>
          {d.pending_requests.map((r: any) => <div className="row" key={r.slot_id} style={{ padding: "8px 0" }}><span className="grow">{fmtDay(r.date)} · {r.start_time}–{r.end_time} · {r.tic_name}</span><StatusBadge status="Requested" /></div>)}
        </div>
      )}
      <div className="card">
        {d.meetings.length === 0 ? <Empty title="No meetings yet">Open a query that has a teacher assigned to request one.</Empty> :
          d.meetings.map((m: any) => <div className="row" key={m.meeting_id} style={{ padding: "8px 0" }}><span className="grow">{fmtDay(m.date)} · {m.start_time}–{m.end_time} · {m.tic_name}</span><StatusBadge status={m.status} /></div>)}
      </div>
    </div>
  );
}

export default function StudentDashboard() {
  const toast = useToast();
  const [tab, setTab] = useState("ask");
  const [queries, setQueries] = useState<any[] | null>(null);
  const [sel, setSel] = useState<string | null>(null);
  const [depts, setDepts] = useState<any[]>([]);
  const [raise, setRaise] = useState<{ text: string; dept?: string | null; ai: boolean } | null>(null);

  const load = useCallback(async () => {
    try { setQueries((await api("/student/queries")).data); } catch (e) { toast(clean(e), true); setQueries([]); }
  }, [toast]);
  useEffect(() => { load(); api("/departments").then(setDepts).catch(() => {}); }, [load]);

  const openQuery = (id: string) => { setTab("queries"); setSel(id); setRaise(null); };
  const tabs = [{ id: "ask", label: "Ask the college" }, { id: "queries", label: `My queries${queries?.length ? ` (${queries.length})` : ""}` }, { id: "meetings", label: "Meetings" }];

  return (
    <Shell role="Student" tabs={tabs} tab={tab} onTab={(t) => { setTab(t); setRaise(null); }} onOpenQuery={openQuery}>
      {raise ? (
        <RaiseForm initial={raise.text} dept={raise.dept} fromAi={raise.ai} depts={depts} onCancel={() => setRaise(null)}
          onDone={(id: string) => { setRaise(null); load(); openQuery(id); }} />
      ) : tab === "ask" ? (
        <Ask depts={depts} onRaise={(q, dept, ai) => setRaise({ text: q, dept, ai: !!ai })} />
      ) : tab === "queries" ? (
        queries === null ? <div className="card muted">Loading…</div> : (
          <div className="split">
            <div>
              <div className="row" style={{ marginBottom: 12 }}><h2 className="grow">My queries</h2><button className="btn sm" onClick={() => setRaise({ text: "", ai: false })}>New query</button></div>
              <QueryList items={queries} selected={sel} onSelect={setSel} empty="You haven’t raised any queries yet" />
            </div>
            <div>{sel ? <QueryDetail id={sel} role="Student" onChanged={load} /> : <div className="card"><Empty title="Select a query">Its progress, documents and meetings appear here.</Empty></div>}</div>
          </div>
        )
      ) : <Meetings />}
    </Shell>
  );
}

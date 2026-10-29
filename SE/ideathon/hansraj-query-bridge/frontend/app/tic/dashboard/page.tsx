"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import Shell from "@/components/Shell";
import QueryDetail, { QueryList } from "@/components/QueryDetail";
import KbManager from "@/components/KbManager";
import { Empty, StatusBadge, useToast } from "@/components/ui";
import { api, clean, fmtDay } from "@/lib/api";

const today = () => new Date().toISOString().slice(0, 10);

function Assigned({ openId }: { openId: string | null }) {
  const toast = useToast();
  const [items, setItems] = useState<any[] | null>(null);
  const [sel, setSel] = useState<string | null>(openId);
  const load = useCallback(async () => {
    try { setItems((await api("/tic/queries")).data); } catch (e) { toast(clean(e), true); setItems([]); }
  }, [toast]);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { if (openId) setSel(openId); }, [openId]);
  return (
    <div className="split">
      <div>
        <h2 style={{ marginBottom: 12 }}>Assigned to you</h2>
        {items === null ? <div className="card muted">Loading…</div> : <QueryList items={items} selected={sel} onSelect={setSel} showStudent empty="Nothing assigned yet" />}
      </div>
      <div>{sel ? <QueryDetail id={sel} role="TIC" onChanged={load} /> : <div className="card"><Empty title="Select a query">Request documents, schedule a meeting or resolve it.</Empty></div>}</div>
    </div>
  );
}

function Schedule() {
  const toast = useToast();
  const [date, setDate] = useState(today());
  const [free, setFree] = useState<any[] | null>(null);
  const [slots, setSlots] = useState<any[]>([]);
  const [meetings, setMeetings] = useState<any[]>([]);
  const [cs, setCs] = useState({ start: "", end: "" });

  const load = useCallback(async () => {
    try {
      const [t, s, m] = await Promise.all([api(`/tic/timetable?date=${date}`), api(`/tic/slots?date=${date}`), api("/tic/meetings")]);
      setFree(t.data); setSlots(s); setMeetings(m);
    } catch (e) { toast(clean(e), true); setFree([]); }
  }, [date, toast]);
  useEffect(() => { load(); }, [load]);

  async function publish(start: string, end: string) {
    try { await api("/tic/slots", { body: { date, start_time: start, end_time: end } }); toast("Slot published for students."); load(); }
    catch (e) { toast(clean(e), true); }
  }
  async function custom(e: FormEvent) { e.preventDefault(); await publish(cs.start, cs.end); }
  async function accept(id: string) {
    try { await api(`/tic/slots/${id}/accept`, { method: "POST" }); toast("Meeting accepted. The student has been notified."); load(); }
    catch (e) { toast(clean(e), true); }
  }
  async function cancel(id: string) {
    try { await api(`/tic/meetings/${id}/cancel`, { method: "POST" }); toast("Meeting cancelled."); load(); }
    catch (e) { toast(clean(e), true); }
  }
  const requested = slots.filter((s) => s.status === "Requested");
  return (
    <div className="split" style={{ gridTemplateColumns: "minmax(300px, 420px) 1fr" }}>
      <div>
        <h2 style={{ marginBottom: 12 }}>Availability</h2>
        <div className="card">
          <div className="field" style={{ maxWidth: 220 }}><label htmlFor="td">Date</label><input id="td" type="date" min={today()} value={date} onChange={(e) => setDate(e.target.value)} /></div>
          <h3>Free periods</h3>
          {free === null ? <p className="muted">Loading…</p> : free.length === 0 ? <p className="muted small">No free periods on this date (weekend, holiday or fully booked).</p> :
            <div className="chips">{free.map((p) => <button key={p.start_time} className="chip" onClick={() => publish(p.start_time, p.end_time)} title="Publish this period as a bookable slot">Publish {p.start_time}–{p.end_time}</button>)}</div>}
          <form onSubmit={custom} className="row" style={{ marginTop: 14, alignItems: "flex-end" }}>
            <div className="field" style={{ margin: 0 }}><label htmlFor="cs">From</label><input id="cs" type="time" value={cs.start} onChange={(e) => setCs({ ...cs, start: e.target.value })} required /></div>
            <div className="field" style={{ margin: 0 }}><label htmlFor="ce">To</label><input id="ce" type="time" value={cs.end} onChange={(e) => setCs({ ...cs, end: e.target.value })} required /></div>
            <button className="btn sm ghost">Publish custom slot</button>
          </form>
          <p className="hint" style={{ marginTop: 8 }}>Slots must sit inside a free period from the college timetable.</p>
        </div>
        <div className="card">
          <h3>Slots on {fmtDay(date)}</h3>
          {slots.length === 0 ? <p className="muted small">None published.</p> : slots.map((s) => <div key={s.slot_id} className="row" style={{ padding: "6px 0" }}><span className="grow">{s.start_time}–{s.end_time}{s.student_name ? ` · ${s.student_name}` : ""}</span><StatusBadge status={s.status} /></div>)}
        </div>
      </div>
      <div>
        <h2 style={{ marginBottom: 12 }}>Requests & meetings</h2>
        {requested.length > 0 && (
          <div className="card"><h3>Meeting requests</h3>
            {requested.map((s) => <div key={s.slot_id} className="row" style={{ padding: "8px 0" }}><span className="grow">{fmtDay(s.date)} · {s.start_time}–{s.end_time} · {s.student_name}</span><button className="btn sm" onClick={() => accept(s.slot_id)}>Accept</button></div>)}
          </div>
        )}
        <div className="card"><h3>Scheduled meetings</h3>
          {meetings.length === 0 ? <Empty title="No meetings yet" /> : meetings.map((m) => (
            <div key={m.meeting_id} className="row" style={{ padding: "8px 0" }}>
              <span className="grow">{fmtDay(m.date)} · {m.start_time}–{m.end_time} · {m.student_name}</span><StatusBadge status={m.status} />
              {m.status === "Scheduled" && <button className="btn sm ghost" onClick={() => cancel(m.meeting_id)}>Cancel</button>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function TicDashboard() {
  const [tab, setTab] = useState("assigned");
  const [openId, setOpenId] = useState<string | null>(null);
  const [canKb, setCanKb] = useState(false);
  useEffect(() => { api("/me").then((m) => setCanKb(!!m.kb_permission)).catch(() => {}); }, []);
  const tabs = [{ id: "assigned", label: "Assigned queries" }, { id: "schedule", label: "Meetings & availability" }, ...(canKb ? [{ id: "kb", label: "Knowledge base" }] : [])];
  return (
    <Shell role="TIC" tabs={tabs} tab={tab} onTab={setTab} onOpenQuery={(id) => { setTab("assigned"); setOpenId(id); }}>
      {tab === "assigned" && <Assigned openId={openId} />}
      {tab === "schedule" && <Schedule />}
      {tab === "kb" && <div><h2 style={{ marginBottom: 12 }}>Knowledge base</h2><KbManager /></div>}
    </Shell>
  );
}

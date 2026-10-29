"use client";
import { FormEvent, useEffect, useState } from "react";
import { api, clean, getSession, setSession } from "@/lib/api";

const DEMO = [["Student", "student.aarav"], ["Teacher-in-Charge", "tic.cs"], ["Admin", "admin.office"]];

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const s = getSession();
    if (s) window.location.replace(`/${s.user.role.toLowerCase()}/dashboard`);
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      const r = await api("/auth/login", { body: { username: username.trim(), password } });
      setSession({ token: r.token, user: r.user });
      window.location.replace(r.dashboard_url.toLowerCase());
    } catch (err) {
      setError(clean(err));
    } finally { setBusy(false); }
  }

  return (
    <main className="login">
      <section className="side" aria-label="About">
        <div className="wordmark">Hansraj Query Bridge<small>Hansraj College</small></div>
        <div>
          <h1>Ask once. Reach the right person.</h1>
          <p style={{ marginTop: 14 }}>Get a verified answer instantly. If there isn’t one, your question goes to the teacher who can resolve it, and you can follow it every step of the way.</p>
        </div>
        <ul>
          <li>Answers come only from information the college has verified</li>
          <li>Upload requested documents securely, without a trip to the office</li>
          <li>Book a meeting with your teacher-in-charge</li>
        </ul>
      </section>
      <section className="form">
        <form onSubmit={submit} aria-labelledby="signin">
          <h2 id="signin" style={{ marginBottom: 4 }}>Sign in</h2>
          <p className="muted" style={{ marginBottom: 20 }}>Use your college username and password.</p>
          {error && <div className="alert bad" role="alert">{error}</div>}
          <div className="field">
            <label htmlFor="u">College username</label>
            <input id="u" type="text" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="p">Password</label>
            <input id="p" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn" style={{ width: "100%" }} disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
          <div className="demo muted">
            Demo accounts (password <code>Hansraj@123</code>):<br />
            {DEMO.map(([l, u]) => <button type="button" key={u} onClick={() => { setUsername(u); setPassword("Hansraj@123"); }}>{l}</button>)}
          </div>
        </form>
      </section>
    </main>
  );
}

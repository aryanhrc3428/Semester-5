"use client";
import { createContext, useCallback, useContext, useState, ReactNode } from "react";

const STATUS_CLASS: Record<string, string> = {
  "Open": "b-open", "Assigned to TIC": "b-assigned", "Documents Required": "b-docs", "Document Submitted": "b-submitted",
  "Resolved": "b-resolved", "Pending Review": "b-submitted", "Verified": "b-verified", "Rejected": "b-rejected",
  "Scheduled": "b-scheduled", "Cancelled": "b-cancelled", "Available": "b-active", "Requested": "b-open", "Accepted": "b-accepted",
  "Active": "b-active", "Inactive": "b-inactive", "Archived": "b-archived",
};
// The SRS calls a fresh query "New"; the workflow stores "Open".
const STATUS_LABEL: Record<string, string> = { "Open": "New", "Assigned to TIC": "With teacher" };

export function StatusBadge({ status }: { status: string }) {
  return <span className={`badge ${STATUS_CLASS[status] || "b-neutral"}`}>{STATUS_LABEL[status] || status}</span>;
}

const FLOW = ["Open", "Assigned to TIC", "Documents Required", "Resolved"];
const FLOW_LABEL = ["Submitted", "With teacher", "Documents", "Resolved"];
export function Progress({ status }: { status: string }) {
  const idx = status === "Document Submitted" ? 2 : FLOW.indexOf(status);
  return (
    <ol className="steps" aria-label={`Progress: ${STATUS_LABEL[status] || status}`}>
      {FLOW_LABEL.map((l, i) => <li key={l} className={i < idx || status === "Resolved" ? "done" : i === idx ? "now" : ""}>{l}</li>)}
    </ol>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return <div className="empty"><b>{title}</b>{children}</div>;
}

type Toast = { id: number; text: string; bad?: boolean };
const ToastCtx = createContext<(text: string, bad?: boolean) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const push = useCallback((text: string, bad?: boolean) => {
    const id = Date.now() + Math.random();
    setItems((x) => [...x, { id, text, bad }]);
    setTimeout(() => setItems((x) => x.filter((t) => t.id !== id)), bad ? 6000 : 3500);
  }, []);
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {items.map((t) => <div key={t.id} className={`toast ${t.bad ? "bad" : ""}`}>{t.text}</div>)}
      </div>
    </ToastCtx.Provider>
  );
}

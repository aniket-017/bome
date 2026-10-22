import { useState } from "react";
import { BomImageUpload } from "../components/BomImageUpload";
import { BomUpload } from "../components/BomUpload";
import { ManualBomGrid } from "../components/ManualBomGrid";

type Tab = "excel" | "manual" | "image";

const TABS: { id: Tab; label: string }[] = [
  { id: "excel", label: "Upload Excel / CSV" },
  { id: "manual", label: "Enter manually" },
  { id: "image", label: "From image" },
];

export function BomNewPage() {
  const [tab, setTab] = useState<Tab>("excel");
  return (
    <div className="page">
      <header className="page-header">
        <h1>New BOM</h1>
      </header>
      <div className="tabs">
        {TABS.map((t) => (
          <button key={t.id} className={`tab ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      <section className="card">
        {tab === "excel" && <BomUpload />}
        {tab === "manual" && <ManualBomGrid />}
        {tab === "image" && <BomImageUpload />}
      </section>
    </div>
  );
}

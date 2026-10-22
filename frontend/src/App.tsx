import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { BomDetailPage } from "./pages/BomDetailPage";
import { BomListPage } from "./pages/BomListPage";
import { BomNewPage } from "./pages/BomNewPage";
import { PartsSearchPage } from "./pages/PartsSearchPage";

export default function App() {
  return (
    <div className="app">
      <nav className="topnav">
        <span className="brand">BOM Matcher</span>
        <NavLink to="/parts">Parts search</NavLink>
        <NavLink to="/boms" end>
          BOMs
        </NavLink>
        <NavLink to="/boms/new">New BOM</NavLink>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/boms" replace />} />
          <Route path="/parts" element={<PartsSearchPage />} />
          <Route path="/boms" element={<BomListPage />} />
          <Route path="/boms/new" element={<BomNewPage />} />
          <Route path="/boms/:id" element={<BomDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}

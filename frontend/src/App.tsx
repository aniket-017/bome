import { Link, NavLink, Route, Routes } from "react-router-dom";
import { COMING_SOON, MODULES } from "./modules";
import { BomCostingPage } from "./pages/BomCostingPage";
import { BomDetailPage } from "./pages/BomDetailPage";
import { BomListPage } from "./pages/BomListPage";
import { BomNewPage } from "./pages/BomNewPage";
import { ComingSoonPage } from "./pages/ComingSoonPage";
import { GrnDetailPage } from "./pages/GrnDetailPage";
import { GrnFormPage } from "./pages/GrnFormPage";
import { GrnListPage } from "./pages/GrnListPage";
import { HomePage } from "./pages/HomePage";
import { ItemMasterPage } from "./pages/ItemMasterPage";
import { MrDetailPage } from "./pages/MrDetailPage";
import { MrFormPage } from "./pages/MrFormPage";
import { MrListPage } from "./pages/MrListPage";
import { PartsSearchPage } from "./pages/PartsSearchPage";
import { StockPage } from "./pages/StockPage";

export default function App() {
  return (
    <div className="app">
      <header className="topnav">
        <Link to="/" className="brand">
          BOM ERP
        </Link>
        <span className="topnav-sub">Item Master · BOM · Estimation · Inventory</span>
      </header>
      <div className="app-body">
        <Sidebar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/items" element={<ItemMasterPage />} />
            <Route path="/parts" element={<PartsSearchPage />} />
            <Route path="/boms" element={<BomListPage />} />
            <Route path="/boms/new" element={<BomNewPage />} />
            <Route path="/boms/:id" element={<BomDetailPage />} />
            <Route path="/boms/:id/costing" element={<BomCostingPage mode="cost" />} />
            <Route path="/estimation/bom-costing" element={<BomCostingPage mode="cost" />} />
            <Route path="/estimation/quantity" element={<BomCostingPage mode="quantity" />} />
            <Route path="/inventory/grn" element={<GrnListPage />} />
            <Route path="/inventory/grn/new" element={<GrnFormPage />} />
            <Route path="/inventory/grn/:id" element={<GrnDetailPage />} />
            <Route path="/inventory/mr" element={<MrListPage />} />
            <Route path="/inventory/mr/new" element={<MrFormPage />} />
            <Route path="/inventory/mr/:id" element={<MrDetailPage />} />
            <Route path="/inventory/stock" element={<StockPage />} />
            {COMING_SOON.map(({ module, item }) => (
              <Route key={item.to} path={item.to} element={<ComingSoonPage module={module} item={item} />} />
            ))}
            <Route path="*" element={<div className="page">Page not found. <Link to="/">Go home</Link></div>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <nav className="sidebar">
      <NavLink to="/" end className="side-link home-link">
        Home
      </NavLink>
      {MODULES.map((m) => (
        <div key={m.key} className="side-group">
          <div className="side-title">{m.label}</div>
          {m.items.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.to === "/boms" || item.to === "/items"}
              className={`side-link ${item.enabled ? "" : "soon"}`}
              title={item.description}
            >
              {item.label}
              {!item.enabled && <span className="soon-tag">Soon</span>}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}

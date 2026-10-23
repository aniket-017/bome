export interface ModuleItem {
  label: string;
  to: string;
  enabled: boolean;
  description?: string;
}

export interface ErpModule {
  key: string;
  label: string;
  description: string;
  example: string;
  items: ModuleItem[];
}

export const MODULES: ErpModule[] = [
  {
    key: "items",
    label: "Item Master",
    description: "Central database of all materials, components and finished products.",
    example: "MS plate, bolts, bearings, motors, CNC machines.",
    items: [
      { label: "Search / Add / Modify", to: "/items", enabled: true },
      { label: "Parts search", to: "/parts", enabled: true },
    ],
  },
  {
    key: "bom",
    label: "Bill of Materials",
    description: "The materials and quantities needed to manufacture a product.",
    example: "A machine assembly needs 10 bolts, 2 bearings and 1 motor.",
    items: [
      { label: "BOMs", to: "/boms", enabled: true },
      { label: "New BOM", to: "/boms/new", enabled: true },
    ],
  },
  {
    key: "estimation",
    label: "Estimation",
    description: "Expected material, labour and manufacturing cost of a product or job.",
    example: "Estimating the cost to manufacture a machine frame.",
    items: [
      {
        label: "BOM Costing", to: "/estimation/bom-costing", enabled: true,
        description: "Cost of all materials in a BOM: steel + bearings + other components.",
      },
      {
        label: "Quantity Estimation", to: "/estimation/quantity", enabled: true,
        description: "Quantities needed for a batch: 20 assemblies x 4 bolts = 80 bolts.",
      },
      {
        label: "Weight Estimation", to: "/estimation/weight", enabled: false,
        description: "Expected weight of raw materials or components, e.g. a steel plate before purchasing it.",
      },
      {
        label: "Welding Costing", to: "/estimation/welding", enabled: false,
        description: "Welding labour, consumables and machine time for a fabricated structure.",
      },
      {
        label: "Machining Cost", to: "/estimation/machining", enabled: false,
        description: "Turning, milling, drilling, grinding and CNC time, e.g. 2 h at 1,000/h = 2,000.",
      },
    ],
  },
  {
    key: "inventory",
    label: "Inventory",
    description: "Materials received, issued and available in stock.",
    example: "Checking how many kilograms of steel are available.",
    items: [
      { label: "GRN Entry", to: "/inventory/grn", enabled: true, description: "Goods Receipt Note: materials received from a supplier." },
      { label: "MR Entry & Issue", to: "/inventory/mr", enabled: true, description: "Material Requisition for a job or department, then issue from stock." },
      { label: "Stock", to: "/inventory/stock", enabled: true, description: "Quantity and value currently in stock." },
    ],
  },
  {
    key: "planning",
    label: "Planning",
    description: "Organises sales requirements, materials, production and shop-floor activities.",
    example: "Planning what to manufacture next week.",
    items: [
      { label: "Sales Planning", to: "/planning/sales", enabled: false, description: "Forecast customer demand and sales orders." },
      { label: "Material Planning", to: "/planning/material", enabled: false, description: "Which materials are required and when to procure them." },
      { label: "Production Planning", to: "/planning/production", enabled: false, description: "What to manufacture, in what quantities, and by when." },
      { label: "Shop Planning", to: "/planning/shop", enabled: false, description: "Allocate shop-floor jobs, machines, operators and work sequences." },
    ],
  },
  {
    key: "pricing",
    label: "Price List / Quotation",
    description: "Selling prices and price offers for customers.",
    example: "Quoting 2,50,000 for a fabricated assembly.",
    items: [
      { label: "Price List", to: "/pricing/price-list", enabled: false, description: "A predefined list of item selling prices." },
      { label: "Quotation", to: "/pricing/quotation", enabled: false, description: "A formal offer with prices, quantities, taxes, delivery and payment terms." },
    ],
  },
  {
    key: "stationery",
    label: "Stationery Formats",
    description: "Standard document templates for purchasing, receiving and issuing materials.",
    example: "PR, PO, GRN and Material Requisition forms.",
    items: [
      { label: "PR - Purchase Requisition", to: "/stationery/pr", enabled: false, description: "An internal request to purchase materials or services." },
      { label: "PO - Purchase Order", to: "/stationery/po", enabled: false, description: "A formal order sent to a supplier." },
      { label: "GRN - Goods Receipt Note", to: "/inventory/grn", enabled: true },
      { label: "MR & Issue", to: "/inventory/mr", enabled: true },
    ],
  },
  {
    key: "charts",
    label: "Material Charts",
    description: "Reports and visual summaries of material quantities, usage and requirements.",
    example: "A chart showing steel requirements by job.",
    items: [{ label: "Material Charts", to: "/charts", enabled: false }],
  },
  {
    key: "lean",
    label: "Lean Manufacturing",
    description: "Methods to reduce waste, waiting, excess inventory and unnecessary work.",
    example: "Reducing material wastage during cutting.",
    items: [{ label: "Lean Manufacturing", to: "/lean", enabled: false }],
  },
  {
    key: "opex",
    label: "Operational Excellence",
    description: "Improving quality, productivity, delivery, safety and cost efficiency.",
    example: "Reducing machine downtime and rejected components.",
    items: [{ label: "Operational Excellence", to: "/opex", enabled: false }],
  },
  {
    key: "skills",
    label: "Skills & Learning",
    description: "Training, skill development and learning resources for employees.",
    example: "Training operators to use CNC machines safely.",
    items: [{ label: "Skills & Learning", to: "/skills", enabled: false }],
  },
];

export interface WorkflowStep {
  title: string;
  detail: string;
  to: string;
  enabled: boolean;
}

export const WORKFLOW: WorkflowStep[] = [
  { title: "Item Master", detail: "Define materials and products.", to: "/items", enabled: true },
  { title: "BOM", detail: "Define components and quantities.", to: "/boms", enabled: true },
  { title: "Estimation", detail: "Calculate material and production costs.", to: "/estimation/bom-costing", enabled: true },
  { title: "Quotation / Sales Order", detail: "Offer a price and confirm customer demand.", to: "/pricing/quotation", enabled: false },
  { title: "Material Planning", detail: "Check stock and purchase shortages.", to: "/estimation/quantity", enabled: true },
  { title: "PR > PO > GRN", detail: "Procure and receive materials.", to: "/inventory/grn", enabled: true },
  { title: "Production / Shop Planning", detail: "Schedule and manufacture the product.", to: "/planning/production", enabled: false },
  { title: "Inventory & Cost Review", detail: "Track issues, stock and actual costs.", to: "/inventory/stock", enabled: true },
];

/** Placeholder routes: every disabled item, each with the module it belongs to. */
export const COMING_SOON = MODULES.flatMap((m) => m.items.filter((i) => !i.enabled).map((item) => ({ module: m, item })));

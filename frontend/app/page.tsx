"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type TrendRecord = { state: string; category: string; total_orders: number; total_revenue: number };
type DemandRecord = { state: string; city: string; product_name: string; category: string; demand_score: number };
type MismatchRecord = { state: string; city: string; product_name: string; available_stock: number; demand_score: number; sdr: number; status: string };
type Tab = "regional-trends" | "demand-scores" | "supply-demand";

const demoTrends: TrendRecord[] = [
  { state: "Maharashtra", category: "Electronics", total_orders: 18420, total_revenue: 4825000 },
  { state: "Karnataka", category: "Fashion", total_orders: 15280, total_revenue: 3268000 },
  { state: "Telangana", category: "Home & Living", total_orders: 12140, total_revenue: 2914000 },
  { state: "Delhi", category: "Electronics", total_orders: 10870, total_revenue: 2786000 },
  { state: "Tamil Nadu", category: "Beauty", total_orders: 9670, total_revenue: 1842000 },
  { state: "Gujarat", category: "Fashion", total_orders: 8430, total_revenue: 1679000 },
];
const demoDemand: DemandRecord[] = [
  { state: "Maharashtra", city: "Mumbai", product_name: "Wireless Earbuds", category: "Electronics", demand_score: .9421 },
  { state: "Karnataka", city: "Bengaluru", product_name: "Running Shoes", category: "Fashion", demand_score: .8874 },
  { state: "Telangana", city: "Hyderabad", product_name: "Air Fryer", category: "Home & Living", demand_score: .8238 },
  { state: "Delhi", city: "New Delhi", product_name: "Smart Watch", category: "Electronics", demand_score: .7912 },
  { state: "Tamil Nadu", city: "Chennai", product_name: "Skin Care Set", category: "Beauty", demand_score: .7345 },
];
const demoMismatch: MismatchRecord[] = [
  { state: "Maharashtra", city: "Mumbai", product_name: "Wireless Earbuds", available_stock: 128, demand_score: .9421, sdr: .31, status: "CRITICAL_SHORTAGE" },
  { state: "Karnataka", city: "Bengaluru", product_name: "Running Shoes", available_stock: 940, demand_score: .8874, sdr: 1.42, status: "BALANCED" },
  { state: "Telangana", city: "Hyderabad", product_name: "Air Fryer", available_stock: 1840, demand_score: .8238, sdr: 2.61, status: "EXCESS_INVENTORY" },
  { state: "Delhi", city: "New Delhi", product_name: "Smart Watch", available_stock: 210, demand_score: .7912, sdr: .58, status: "CRITICAL_SHORTAGE" },
  { state: "Tamil Nadu", city: "Chennai", product_name: "Skin Care Set", available_stock: 560, demand_score: .7345, sdr: 1.08, status: "BALANCED" },
];
const compact = (n: number) => Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(n);
const money = (n: number) => `₹${(n / 100000).toFixed(1)}L`;

function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-white/[0.07] bg-[#101116] p-5 shadow-[0_12px_35px_rgba(0,0,0,.18)] ${className}`}>{children}</section>;
}
function PanelTitle({ eyebrow, title, side }: { eyebrow?: string; title: string; side?: React.ReactNode }) {
  return <div className="mb-5 flex items-start justify-between gap-3"><div>{eyebrow && <p className="mb-1 text-[10px] font-semibold uppercase tracking-[.18em] text-zinc-500">{eyebrow}</p>}<h2 className="text-sm font-semibold text-zinc-100">{title}</h2></div>{side}</div>;
}
function Pill({ children, tone = "green" }: { children: React.ReactNode; tone?: "green" | "yellow" | "red" | "blue" | "muted" }) {
  const colors = { green: "bg-emerald-400/10 text-emerald-300", yellow: "bg-amber-400/10 text-amber-300", red: "bg-rose-400/10 text-rose-300", blue: "bg-cyan-400/10 text-cyan-300", muted: "bg-white/[0.06] text-zinc-400" };
  return <span className={`inline-flex rounded-full px-2 py-1 text-[10px] font-medium ${colors[tone]}`}>{children}</span>;
}
function Bars({ values, labels, color = "#35e6a1" }: { values: number[]; labels: string[]; color?: string }) {
  const max = Math.max(...values, 1);
  return <div className="flex h-44 items-end gap-2 sm:gap-3">{values.map((value, i) => <div key={`${labels[i]}-${i}`} className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2"><div className="flex h-full w-full items-end"><div title={`${labels[i]}: ${value.toLocaleString("en-IN")}`} className="w-full rounded-t-md transition-all" style={{ height: `${Math.max(5, value / max * 100)}%`, background: `linear-gradient(180deg, ${color}, ${color}55)` }} /></div><span className="w-full truncate text-center text-[9px] text-zinc-500">{labels[i]}</span></div>)}</div>;
}
function Sparkline({ values, color = "#35e6a1" }: { values: number[]; color?: string }) {
  const max = Math.max(...values), min = Math.min(...values), range = max - min || 1;
  const points = values.map((v, i) => `${i / (values.length - 1) * 280},${58 - (v - min) / range * 48}`).join(" ");
  return <svg viewBox="0 0 280 64" className="h-14 w-full" preserveAspectRatio="none"><polyline points={points} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke" /></svg>;
}

export default function HomePage() {
  const [trends, setTrends] = useState<TrendRecord[]>(demoTrends);
  const [demand, setDemand] = useState<DemandRecord[]>(demoDemand);
  const [mismatch, setMismatch] = useState<MismatchRecord[]>(demoMismatch);
  const [tab, setTab] = useState<Tab>("regional-trends");
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<"demo" | "live">("demo");
  const [sourceMessage, setSourceMessage] = useState("Illustrative preview data · API connection pending");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const urls = ["http://localhost:5000/api/regional-trends", "http://localhost:5000/api/demand-scores", "http://localhost:5000/api/supply-demand"];
        const responses = await Promise.all(urls.map(url => fetch(url)));
        if (responses.some(r => !r.ok)) throw new Error("Analytics API unavailable");
        const payloads = await Promise.all(responses.map(r => r.json()));
        if (payloads.some(p => p.status !== "success" || !Array.isArray(p.data))) throw new Error("Unexpected API response");
        if (!cancelled) {
          setTrends(payloads[0].data); setDemand(payloads[1].data); setMismatch(payloads[2].data);
          setSource("live"); setSourceMessage(`Live Flask API · updated ${new Date().toLocaleTimeString()}`);
        }
      } catch {
        if (!cancelled) { setSource("demo"); setSourceMessage("Demo values shown · start the Flask API for live data"); }
      }
    }
    load(); return () => { cancelled = true; };
  }, []);

  const q = query.trim().toLowerCase();
  const filteredTrends = useMemo(() => trends.filter(r => `${r.state} ${r.category}`.toLowerCase().includes(q)), [trends, q]);
  const filteredDemand = useMemo(() => demand.filter(r => `${r.state} ${r.city} ${r.product_name} ${r.category}`.toLowerCase().includes(q)), [demand, q]);
  const filteredMismatch = useMemo(() => mismatch.filter(r => `${r.state} ${r.city} ${r.product_name} ${r.status}`.toLowerCase().includes(q)), [mismatch, q]);
  const totalOrders = trends.reduce((s, r) => s + (Number(r.total_orders) || 0), 0);
  const totalRevenue = trends.reduce((s, r) => s + (Number(r.total_revenue) || 0), 0);
  const shortageCount = mismatch.filter(r => r.status === "CRITICAL_SHORTAGE").length;
  const avgDemand = demand.length ? demand.reduce((s, r) => s + (Number(r.demand_score) || 0), 0) / demand.length : 0;
  const topRegions = [...trends].sort((a, b) => b.total_revenue - a.total_revenue).slice(0, 5);
  const topDemand = [...demand].sort((a, b) => b.demand_score - a.demand_score).slice(0, 5);

  const tabs: { id: Tab; label: string }[] = [{ id: "regional-trends", label: "Regional trends" }, { id: "demand-scores", label: "Demand scores" }, { id: "supply-demand", label: "Stock mismatch" }];

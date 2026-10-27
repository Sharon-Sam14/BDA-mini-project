"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

type TrendRecord = { state: string; category: string; total_orders: number; total_revenue: number };
type DemandRecord = { state: string; city: string; product_name: string; category: string; demand_score: number };
type MismatchRecord = { state: string; city: string; product_name: string; available_stock: number; demand_score: number; sdr: number; status: string };
type Tab = "overview" | "regional-trends" | "demand-scores" | "supply-demand";

const demoTrends: TrendRecord[] = [
  { state: "Maharashtra", category: "Electronics", total_orders: 18420, total_revenue: 4825000 },
  { state: "Karnataka", category: "Fashion", total_orders: 15280, total_revenue: 3268000 },
  { state: "Telangana", category: "Home & Living", total_orders: 12140, total_revenue: 2914000 },
  { state: "Delhi", category: "Electronics", total_orders: 10870, total_revenue: 2786000 },
  { state: "Tamil Nadu", category: "Beauty", total_orders: 9670, total_revenue: 1842000 },
  { state: "Gujarat", category: "Fashion", total_orders: 8430, total_revenue: 1679000 },
];
const demoDemand: DemandRecord[] = [
  { state: "Maharashtra", city: "Mumbai", product_name: "Wireless Earbuds", category: "Electronics", demand_score: 0.9421 },
  { state: "Karnataka", city: "Bengaluru", product_name: "Running Shoes", category: "Fashion", demand_score: 0.8874 },
  { state: "Telangana", city: "Hyderabad", product_name: "Air Fryer", category: "Home & Living", demand_score: 0.8238 },
  { state: "Delhi", city: "New Delhi", product_name: "Smart Watch", category: "Electronics", demand_score: 0.7912 },
  { state: "Tamil Nadu", city: "Chennai", product_name: "Skin Care Set", category: "Beauty", demand_score: 0.7345 },
];
const demoMismatch: MismatchRecord[] = [
  { state: "Maharashtra", city: "Mumbai", product_name: "Wireless Earbuds", available_stock: 128, demand_score: 0.9421, sdr: 0.31, status: "CRITICAL_SHORTAGE" },
  { state: "Karnataka", city: "Bengaluru", product_name: "Running Shoes", available_stock: 940, demand_score: 0.8874, sdr: 1.42, status: "BALANCED" },
  { state: "Telangana", city: "Hyderabad", product_name: "Air Fryer", available_stock: 1840, demand_score: 0.8238, sdr: 2.61, status: "EXCESS_INVENTORY" },
  { state: "Delhi", city: "New Delhi", product_name: "Smart Watch", available_stock: 210, demand_score: 0.7912, sdr: 0.58, status: "CRITICAL_SHORTAGE" },
  { state: "Tamil Nadu", city: "Chennai", product_name: "Skin Care Set", available_stock: 560, demand_score: 0.7345, sdr: 1.08, status: "BALANCED" },
];
const money = (n: number) => `₹${(n / 100000).toFixed(1)}L`;
const compact = (n: number) => Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(n);

function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-white/[0.07] bg-[#101116] p-5 shadow-[0_12px_35px_rgba(0,0,0,.18)] ${className}`}>{children}</section>;
}
function PanelTitle({ eyebrow, title, side }: { eyebrow?: string; title: string; side?: ReactNode }) {
  return <div className="mb-5 flex items-start justify-between gap-3"><div>{eyebrow && <p className="mb-1 text-[10px] font-semibold uppercase tracking-[.18em] text-zinc-500">{eyebrow}</p>}<h2 className="text-sm font-semibold text-zinc-100">{title}</h2></div>{side}</div>;
}
function Pill({ children, tone = "green" }: { children: ReactNode; tone?: "green" | "yellow" | "red" | "blue" | "muted" }) {
  const tones = { green: "bg-emerald-400/10 text-emerald-300", yellow: "bg-amber-400/10 text-amber-300", red: "bg-rose-400/10 text-rose-300", blue: "bg-cyan-400/10 text-cyan-300", muted: "bg-white/[0.06] text-zinc-400" };
  return <span className={`inline-flex rounded-full px-2 py-1 text-[10px] font-medium ${tones[tone]}`}>{children}</span>;
}
function Sparkline({ values, color = "#35e6a1", height = 62 }: { values: number[]; color?: string; height?: number }) {
  const max = Math.max(...values), min = Math.min(...values), range = max - min || 1;
  const points = values.map((v, i) => `${(i / (values.length - 1)) * 280},${height - 5 - ((v - min) / range) * (height - 12)}`).join(" ");
  return <svg viewBox={`0 0 280 ${height}`} className="h-full w-full" preserveAspectRatio="none"><defs><linearGradient id={`fill-${color.replace('#','')}`} x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor={color} stopOpacity=".25"/><stop offset="100%" stopColor={color} stopOpacity="0"/></linearGradient></defs><polygon points={`0,${height} ${points} 280,${height}`} fill={`url(#fill-${color.replace('#','')})`}/><polyline points={points} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke"/></svg>;
}
function BarChart({ values, labels, color = "#29dda0" }: { values: number[]; labels: string[]; color?: string }) {
  const max = Math.max(...values, 1);
  return <div className="flex h-44 items-end gap-2 sm:gap-3">{values.map((v, i) => <div key={labels[i]} className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2"><div className="flex h-full w-full items-end"><div title={`${labels[i]}: ${v.toLocaleString("en-IN")}`} className="w-full rounded-t-md transition-all" style={{ height: `${Math.max(5, (v / max) * 100)}%`, background: `linear-gradient(180deg, ${color}, ${color}55)` }}/></div><span className="w-full truncate text-center text-[9px] text-zinc-500">{labels[i]}</span></div>)}</div>;
}
function HorizontalBars({ rows }: { rows: { label: string; value: number; color?: string }[] }) {
  const max = Math.max(...rows.map(r => r.value), 1);
  return <div className="space-y-4">{rows.map((r) => <div key={r.label}><div className="mb-1.5 flex justify-between gap-3 text-xs"><span className="truncate text-zinc-300">{r.label}</span><span className="shrink-0 font-mono text-zinc-500">{compact(r.value)}</span></div><div className="h-2 overflow-hidden rounded-full bg-white/[0.06]"><div className="h-full rounded-full" style={{ width: `${(r.value / max) * 100}%`, background: r.color || "#34e6a1" }}/></div></div>)}</div>;
}
function Donut({ percent, color = "#34e6a1", label }: { percent: number; color?: string; label: string }) {
  return <div className="relative grid h-28 w-28 shrink-0 place-items-center"><svg viewBox="0 0 100 100" className="h-full w-full -rotate-90"><circle cx="50" cy="50" r="39" fill="none" stroke="#292a32" strokeWidth="11"/><circle cx="50" cy="50" r="39" fill="none" stroke={color} strokeWidth="11" strokeLinecap="round" strokeDasharray={`${Math.min(100, percent) * 2.45} 245`} /></svg><div className="absolute text-center"><div className="text-xl font-semibold text-white">{percent}%</div><div className="text-[9px] text-zinc-500">{label}</div></div></div>;
}

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<TrendRecord[]>(demoTrends);
  const [demand, setDemand] = useState<DemandRecord[]>(demoDemand);
  const [mismatch, setMismatch] = useState<MismatchRecord[]>(demoMismatch);
  const [tab, setTab] = useState<Tab>("overview");
  const [query, setQuery] = useState("");
  const [range, setRange] = useState("Last 30 days");
  const [source, setSource] = useState<"demo" | "live">("demo");
  const [lastUpdated, setLastUpdated] = useState("Demo data · illustrative values");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const urls = ["http://localhost:5000/api/regional-trends", "http://localhost:5000/api/demand-scores", "http://localhost:5000/api/supply-demand"];
        const responses = await Promise.all(urls.map(url => fetch(url)));
        if (responses.some(r => !r.ok)) throw new Error("One or more analytics endpoints are unavailable");
        const payloads = await Promise.all(responses.map(r => r.json()));
        if (payloads.some(p => p.status !== "success" || !Array.isArray(p.data))) throw new Error("Unexpected API response");
        if (!cancelled) {
          setTrends(payloads[0].data); setDemand(payloads[1].data); setMismatch(payloads[2].data);
          setSource("live"); setLastUpdated(`Live API · refreshed ${new Date().toLocaleTimeString()}`);
        }
      } catch {
        if (!cancelled) { setSource("demo"); setLastUpdated("Demo data · API unavailable, showing illustrative values"); }
      }
    }
    load(); return () => { cancelled = true; };
  }, []);

  // The current Flask endpoints return pre-aggregated rows without timestamps.
  // In preview mode, range presets therefore use clearly-labelled illustrative
  // period estimates so the controls visibly change the charts and KPIs.
  // Live API data is left untouched until date-stamped/event-level data is available.
  const previewFactors: Record<string, { volume: number; demand: number; stock: number }> = {
    "Last 7 days": { volume: 0.24, demand: -0.035, stock: 0.92 },
    "Last 30 days": { volume: 1, demand: 0, stock: 1 },
    "Last 90 days": { volume: 2.65, demand: 0.025, stock: 1.08 },
    "Year to date": { volume: 7.4, demand: 0.045, stock: 1.16 },
  };
  const periodFactor = previewFactors[range] || previewFactors["Last 30 days"];
  const periodTrends = useMemo(() => source === "demo" ? trends.map(r => ({
    ...r,
    total_orders: Math.max(1, Math.round(r.total_orders * periodFactor.volume)),
    total_revenue: Math.max(1, Math.round(r.total_revenue * periodFactor.volume)),
  })) : trends, [trends, source, range]);
  const periodDemand = useMemo(() => source === "demo" ? demand.map((r, i) => ({
    ...r,
    demand_score: Math.max(0.05, Math.min(0.99, r.demand_score + periodFactor.demand + ((i % 2 === 0 ? 1 : -1) * Math.abs(periodFactor.demand) * 0.18))),
  })) : demand, [demand, source, range]);
  const periodMismatch = useMemo(() => source === "demo" ? mismatch.map((r, i) => {
    const available_stock = Math.max(1, Math.round(r.available_stock * periodFactor.stock * (1 + ((i % 3) - 1) * (range === "Last 30 days" ? 0 : 0.035))));
    const demand_score = Math.max(0.05, Math.min(0.99, r.demand_score + periodFactor.demand));
    const sdr = Number((r.sdr * periodFactor.stock / Math.max(0.85, 1 + periodFactor.demand)).toFixed(3));
    const status = sdr < 0.7 ? "CRITICAL_SHORTAGE" : sdr > 2 ? "EXCESS_INVENTORY" : "BALANCED";
    return { ...r, available_stock, demand_score, sdr, status };
  }) : mismatch, [mismatch, source, range]);
  const filteredTrends = useMemo(() => periodTrends.filter(r => `${r.state} ${r.category}`.toLowerCase().includes(query.toLowerCase())), [periodTrends, query]);
  const filteredDemand = useMemo(() => periodDemand.filter(r => `${r.state} ${r.city} ${r.product_name} ${r.category}`.toLowerCase().includes(query.toLowerCase())), [periodDemand, query]);
  const filteredMismatch = useMemo(() => periodMismatch.filter(r => `${r.state} ${r.city} ${r.product_name} ${r.status}`.toLowerCase().includes(query.toLowerCase())), [periodMismatch, query]);
  const totalOrders = periodTrends.reduce((sum, r) => sum + (Number(r.total_orders) || 0), 0);
  const totalRevenue = periodTrends.reduce((sum, r) => sum + (Number(r.total_revenue) || 0), 0);
  const shortageCount = periodMismatch.filter(r => r.status === "CRITICAL_SHORTAGE").length;
  const avgDemand = periodDemand.length ? periodDemand.reduce((sum, r) => sum + (Number(r.demand_score) || 0), 0) / periodDemand.length : 0;
  const topRegions = [...periodTrends].sort((a, b) => b.total_revenue - a.total_revenue).slice(0, 5);
  const topDemand = [...periodDemand].sort((a, b) => b.demand_score - a.demand_score).slice(0, 5);
  const trendBars = periodTrends.slice(0, 7);
  const categoryMap = periodTrends.reduce<Record<string, number>>((acc, row) => { acc[row.category] = (acc[row.category] || 0) + row.total_revenue; return acc; }, {});
  const categoryRows = Object.entries(categoryMap).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([label, value], i) => ({ label, value, color: ["#35e6a1", "#22c8d9", "#9c7bff", "#f5c84b", "#fb7185"][i] }));

  const tabs: { id: Tab; label: string }[] = [{ id: "overview", label: "Overview" }, { id: "regional-trends", label: "Regional trends" }, { id: "demand-scores", label: "Demand scoring" }, { id: "supply-demand", label: "Stock mismatch" }];
  return <main className="min-h-screen bg-[#08090c] px-4 py-5 text-white sm:px-7 lg:px-10">
    <div className="mx-auto max-w-[1500px]">
      <header className="mb-7 flex flex-col gap-5 border-b border-white/[0.08] pb-6 xl:flex-row xl:items-end xl:justify-between">
        <div><div className="mb-3 flex items-center gap-2"><span className="grid h-8 w-8 place-items-center rounded-xl bg-emerald-300 text-sm font-black text-[#07110d]">G</span><span className="text-xs font-semibold uppercase tracking-[.2em] text-zinc-400">GeoCommerce / Analytics</span></div><h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Analytics overview<span className="text-emerald-300">.</span></h1><p className="mt-2 max-w-2xl text-sm text-zinc-400">Location-aware trend detection, regional demand scoring and inventory optimization powered by the Spark analytics pipeline.</p></div>
        <div className="flex flex-wrap items-center gap-2"><span className={`inline-flex items-center gap-2 rounded-full border px-3 py-2 text-[11px] ${source === "live" ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300" : "border-amber-400/20 bg-amber-400/10 text-amber-200"}`}><span className={`h-1.5 w-1.5 rounded-full ${source === "live" ? "bg-emerald-300" : "bg-amber-300"}`}/>{source === "live" ? "Live API connected" : "Preview mode"}</span><select value={range} onChange={e => setRange(e.target.value)} className="rounded-full border border-white/10 bg-[#14151b] px-3 py-2 text-xs text-zinc-300 outline-none"><option>Last 7 days</option><option>Last 30 days</option><option>Last 90 days</option><option>Year to date</option></select><a href="/" className="rounded-full bg-white px-4 py-2 text-xs font-semibold text-black transition hover:bg-emerald-200">Main dashboard ↗</a></div>
      </header>

      <nav className="mb-6 flex gap-1 overflow-x-auto rounded-xl border border-white/[0.07] bg-[#101116] p-1">{tabs.map(t => <button key={t.id} onClick={() => setTab(t.id)} className={`whitespace-nowrap rounded-lg px-4 py-2.5 text-xs transition ${tab === t.id ? "bg-[#25272f] text-white shadow" : "text-zinc-500 hover:text-zinc-200"}`}>{t.label}</button>)}</nav>
      <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><div><p className="text-xs text-zinc-500">{range} <span className="mx-1 text-zinc-700">/</span> India regional dataset</p><p className="mt-1 text-[10px] text-zinc-600">{lastUpdated}</p><p className="mt-1 text-[10px] text-zinc-600">{source === "demo" ? "Preview range estimates · values update with the selected period" : "Live API aggregates · endpoints do not currently include timestamps, so date-range filtering is not applied to live records"}</p></div><div className="relative w-full sm:max-w-xs"><span className="absolute left-3 top-2.5 text-zinc-500">⌕</span><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search state, city, product…" className="w-full rounded-xl border border-white/[0.09] bg-[#101116] py-2.5 pl-9 pr-3 text-xs text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-emerald-300/50"/></div></div>

      {tab === "overview" && <>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Panel><div className="flex items-start justify-between"><span className="text-xs text-zinc-400">Gross merchandise value</span><span className="text-emerald-300">↗</span></div><div className="mt-3 text-3xl font-semibold tracking-tight">{money(totalRevenue)}</div><div className="mt-2 flex items-center gap-2"><Pill>Aggregated GMV</Pill><span className="text-[10px] text-zinc-600">across returned regions</span></div><div className="mt-4 h-10"><Sparkline values={[18, 24, 20, 31, 28, 39, 35, 49, 46, 62]} /></div></Panel>
          <Panel><div className="flex items-start justify-between"><span className="text-xs text-zinc-400">Orders processed</span><span className="text-cyan-300">▥</span></div><div className="mt-3 text-3xl font-semibold tracking-tight">{compact(totalOrders)}</div><div className="mt-2 flex items-center gap-2"><Pill tone="blue">Regional total</Pill><span className="text-[10px] text-zinc-600">all categories</span></div><div className="mt-4 h-10"><Sparkline values={[14, 22, 18, 25, 24, 35, 31, 43, 47, 54]} color="#22c8d9"/></div></Panel>
          <Panel><div className="flex items-start justify-between"><span className="text-xs text-zinc-400">Average demand score</span><span className="text-violet-300">⌁</span></div><div className="mt-3 text-3xl font-semibold tracking-tight">{avgDemand.toFixed(3)}</div><div className="mt-2 flex items-center gap-2"><Pill tone="blue">0–1 index</Pill><span className="text-[10px] text-zinc-600">weighted funnel signal</span></div><div className="mt-4 h-10"><Sparkline values={[28, 36, 33, 45, 42, 48, 57, 53, 65, 72]} color="#a78bfa"/></div></Panel>
          <Panel><div className="flex items-start justify-between"><span className="text-xs text-zinc-400">Critical stock alerts</span><span className="text-rose-300">!</span></div><div className="mt-3 text-3xl font-semibold tracking-tight">{shortageCount.toLocaleString()}</div><div className="mt-2 flex items-center gap-2"><Pill tone={shortageCount ? "red" : "green"}>{shortageCount ? "Needs attention" : "No critical alerts"}</Pill><span className="text-[10px] text-zinc-600">from mismatch results</span></div><div className="mt-4 h-10"><Sparkline values={[55, 45, 52, 37, 42, 28, 35, 20, 24, 15]} color="#fb7185"/></div></Panel>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-12">
          <Panel className="xl:col-span-7"><PanelTitle eyebrow="Regional performance" title="Revenue by region" side={<Pill>₹ GMV</Pill>}/><BarChart values={trendBars.map(r => r.total_revenue)} labels={trendBars.map(r => r.state.split(" ")[0])}/><div className="mt-4 flex items-center justify-between border-t border-white/[0.07] pt-3 text-[10px] text-zinc-500"><span>Aggregated by state and category</span><button onClick={() => setTab("regional-trends")} className="text-emerald-300 hover:text-emerald-200">Explore regions ↗</button></div></Panel>
          <Panel className="xl:col-span-5"><PanelTitle eyebrow="Category mix" title="Revenue contribution"/><div className="flex flex-col items-center gap-6 sm:flex-row"><Donut percent={Math.round((categoryRows[0]?.value || 0) / Math.max(totalRevenue, 1) * 100)} label="Top category"/><div className="w-full space-y-3">{categoryRows.map((r) => <div key={r.label} className="flex items-center justify-between gap-3 text-xs"><div className="flex min-w-0 items-center gap-2"><span className="h-2 w-2 shrink-0 rounded-sm" style={{ background: r.color }}/><span className="truncate text-zinc-300">{r.label}</span></div><span className="font-mono text-zinc-500">{money(r.value)}</span></div>)}</div></div></Panel>
          <Panel className="xl:col-span-5"><PanelTitle eyebrow="Demand intelligence" title="Highest intent products" side={<button onClick={() => setTab("demand-scores")} className="text-[10px] text-emerald-300">View all ↗</button>}/><div className="space-y-4">{topDemand.map((r, i) => <div key={`${r.city}-${r.product_name}`} className="flex items-center gap-3"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-white/[0.05] text-xs text-zinc-400">0{i + 1}</span><div className="min-w-0 flex-1"><div className="truncate text-xs font-medium text-zinc-200">{r.product_name}</div><div className="mt-1 text-[10px] text-zinc-500">{r.city}, {r.state}</div></div><div className="w-20"><div className="mb-1 text-right font-mono text-[10px] text-emerald-300">{Number(r.demand_score).toFixed(3)}</div><div className="h-1.5 rounded-full bg-white/[0.07]"><div className="h-full rounded-full bg-emerald-300" style={{ width: `${Math.max(0, Math.min(100, r.demand_score * 100))}%` }}/></div></div></div>)}</div></Panel>
          <Panel className="xl:col-span-7"><PanelTitle eyebrow="Supply & demand" title="Inventory health by product" side={<button onClick={() => setTab("supply-demand")} className="text-[10px] text-emerald-300">Inspect mismatches ↗</button>}/><div className="overflow-x-auto"><table className="w-full min-w-[520px] text-left text-xs"><thead><tr className="border-b border-white/[0.07] text-[10px] uppercase tracking-wider text-zinc-600"><th className="pb-3 font-medium">Product / region</th><th className="pb-3 text-right font-medium">Stock</th><th className="pb-3 text-right font-medium">Demand</th><th className="pb-3 text-right font-medium">Status</th></tr></thead><tbody>{filteredMismatch.slice(0, 5).map(r => <tr key={`${r.city}-${r.product_name}`} className="border-b border-white/[0.04] last:border-0"><td className="py-3 pr-3"><div className="font-medium text-zinc-200">{r.product_name}</div><div className="mt-1 text-[10px] text-zinc-600">{r.city}, {r.state}</div></td><td className="py-3 text-right font-mono text-zinc-400">{compact(r.available_stock)}</td><td className="py-3 text-right font-mono text-zinc-400">{Number(r.demand_score).toFixed(2)}</td><td className="py-3 text-right"><Pill tone={r.status === "CRITICAL_SHORTAGE" ? "red" : r.status === "EXCESS_INVENTORY" ? "yellow" : "green"}>{r.status.replaceAll("_", " ")}</Pill></td></tr>)}</tbody></table></div></Panel>
        </div>
      </>}

      {tab === "regional-trends" && <div className="grid grid-cols-1 gap-4 xl:grid-cols-12"><Panel className="xl:col-span-7"><PanelTitle eyebrow="Module 01 · Regional trends" title="Revenue by state"/><BarChart values={filteredTrends.map(r => r.total_revenue)} labels={filteredTrends.map(r => r.state.split(" ")[0])} color="#22d3a0"/></Panel><Panel className="xl:col-span-5"><PanelTitle eyebrow="Regional leaderboard" title="Top regions by GMV"/><HorizontalBars rows={topRegions.map(r => ({ label: r.state, value: r.total_revenue }))}/></Panel><Panel className="xl:col-span-12"><PanelTitle title="Regional sales records" side={<Pill>{filteredTrends.length} records</Pill>}/><div className="overflow-x-auto"><table className="w-full min-w-[560px] text-left text-xs"><thead className="text-[10px] uppercase tracking-wider text-zinc-500"><tr className="border-b border-white/[0.08]"><th className="pb-3">State hub</th><th className="pb-3">Category</th><th className="pb-3 text-right">Orders</th><th className="pb-3 text-right">Gross GMV</th></tr></thead><tbody>{filteredTrends.map((r,i)=><tr key={`${r.state}-${r.category}-${i}`} className="border-b border-white/[0.04] last:border-0"><td className="py-3 font-medium text-zinc-200">{r.state}</td><td className="py-3 text-zinc-400">{r.category}</td><td className="py-3 text-right font-mono text-zinc-300">{r.total_orders.toLocaleString()}</td><td className="py-3 text-right font-mono text-emerald-300">₹{r.total_revenue.toLocaleString("en-IN")}</td></tr>)}</tbody></table></div></Panel></div>}

      {tab === "demand-scores" && <div className="grid grid-cols-1 gap-4 xl:grid-cols-12"><Panel className="xl:col-span-5"><PanelTitle eyebrow="Module 02 · Intent engine" title="Demand score distribution"/><div className="space-y-4">{filteredDemand.slice(0,8).map(r=><div key={`${r.city}-${r.product_name}`}><div className="mb-2 flex justify-between gap-3 text-xs"><span className="truncate text-zinc-300">{r.product_name} <span className="text-zinc-600">· {r.city}</span></span><span className="font-mono text-emerald-300">{Number(r.demand_score).toFixed(4)}</span></div><div className="h-2 rounded-full bg-white/[0.07]"><div className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-300" style={{width:`${Math.max(0,Math.min(100,r.demand_score*100))}%`}}/></div></div>)}</div><p className="mt-5 text-[10px] leading-relaxed text-zinc-600">Composite intent score uses the project funnel weighting: 0.15 × Search + 0.20 × View + 0.30 × Cart + 0.35 × Purchase.</p></Panel><Panel className="xl:col-span-7"><PanelTitle title="Demand scoring records" side={<Pill>{filteredDemand.length} records</Pill>}/><div className="overflow-x-auto"><table className="w-full min-w-[560px] text-left text-xs"><thead className="text-[10px] uppercase tracking-wider text-zinc-500"><tr className="border-b border-white/[0.08]"><th className="pb-3">Product</th><th className="pb-3">City / state</th><th className="pb-3">Category</th><th className="pb-3 text-right">Score</th></tr></thead><tbody>{filteredDemand.map((r,i)=><tr key={`${r.city}-${r.product_name}-${i}`} className="border-b border-white/[0.04] last:border-0"><td className="py-3 font-medium text-zinc-200">{r.product_name}</td><td className="py-3 text-zinc-400">{r.city}, {r.state}</td><td className="py-3 text-zinc-500">{r.category}</td><td className="py-3 text-right font-mono text-emerald-300">{Number(r.demand_score).toFixed(4)}</td></tr>)}</tbody></table></div></Panel></div>}

      {tab === "supply-demand" && <div className="grid grid-cols-1 gap-4 xl:grid-cols-12"><Panel className="xl:col-span-4"><PanelTitle eyebrow="Module 03 · Stock health" title="Alert summary"/><div className="space-y-3">{[{label:"Critical shortage",count:periodMismatch.filter(r=>r.status==="CRITICAL_SHORTAGE").length,tone:"red" as const},{label:"Excess inventory",count:periodMismatch.filter(r=>r.status==="EXCESS_INVENTORY").length,tone:"yellow" as const},{label:"Balanced",count:periodMismatch.filter(r=>r.status!=="CRITICAL_SHORTAGE"&&r.status!=="EXCESS_INVENTORY").length,tone:"green" as const}].map(item=><div key={item.label} className="flex items-center justify-between rounded-xl bg-white/[0.03] p-4"><span className="text-xs text-zinc-300">{item.label}</span><Pill tone={item.tone}>{item.count} items</Pill></div>)}</div></Panel><Panel className="xl:col-span-8"><PanelTitle title="Supply-demand mismatch records" side={<Pill>{filteredMismatch.length} records</Pill>}/><div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-xs"><thead className="text-[10px] uppercase tracking-wider text-zinc-500"><tr className="border-b border-white/[0.08]"><th className="pb-3">City / state</th><th className="pb-3">Product</th><th className="pb-3 text-right">Stock</th><th className="pb-3 text-right">Demand</th><th className="pb-3 text-right">SDR</th><th className="pb-3 text-right">Status</th></tr></thead><tbody>{filteredMismatch.map((r,i)=><tr key={`${r.city}-${r.product_name}-${i}`} className="border-b border-white/[0.04] last:border-0"><td className="py-3 text-zinc-300">{r.city}, {r.state}</td><td className="py-3 font-medium text-zinc-200">{r.product_name}</td><td className="py-3 text-right font-mono text-zinc-400">{r.available_stock.toLocaleString()}</td><td className="py-3 text-right font-mono text-zinc-400">{Number(r.demand_score).toFixed(3)}</td><td className="py-3 text-right font-mono text-zinc-400">{Number(r.sdr).toFixed(3)}</td><td className="py-3 text-right"><Pill tone={r.status==="CRITICAL_SHORTAGE"?"red":r.status==="EXCESS_INVENTORY"?"yellow":"green"}>{r.status.replaceAll("_"," ")}</Pill></td></tr>)}</tbody></table></div></Panel></div>}

      <footer className="mt-7 flex flex-col gap-2 border-t border-white/[0.07] pt-4 text-[10px] text-zinc-600 sm:flex-row sm:items-center sm:justify-between"><span>Geo-Spatial E-Commerce Analytics · Apache Spark / PySpark / Spark SQL</span><span>Parquet · HDFS · Location-aware trend detection</span></footer>
    </div>
  </main>;
}

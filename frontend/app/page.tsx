// frontend/app/page.tsx
"use client";

import React, { useEffect, useState } from "react";

// ==========================================
// DATA TYPE SCHEMAS MAPPING PYSPARK STRUCTS
// ==========================================
interface TrendRecord {
  state: string;
  category: string;
  total_orders: number;
  total_revenue: number;
}

interface DemandRecord {
  state: string;
  city: string;
  product_name: string;
  category: string;
  demand_score: number;
}

interface MismatchRecord {
  state: string;
  city: string;
  product_name: string;
  available_stock: number;
  demand_score: number;
  sdr: number;
  status: string;
}

type TabType = "regional-trends" | "demand-scores" | "supply-demand";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>("regional-trends");
  const [trends, setTrends] = useState<TrendRecord[]>([]);
  const [demandScores, setDemandScores] = useState<DemandRecord[]>([]);
  const [mismatchData, setMismatchData] = useState<MismatchRecord[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Unified Search State Hook
  const [searchQuery, setSearchQuery] = useState<string>("");

  // ==========================================
  // ASYNCHRONOUS DATA INGESTION ENGINE (FLASK)
  // ==========================================
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch Pipeline Module 1: Regional Sales Aggregates
        const trendsRes = await fetch(
          "http://localhost:5000/api/regional-trends",
        );
        if (!trendsRes.ok)
          throw new Error(
            `Trends API returned error status: ${trendsRes.status}`,
          );
        const trendsPayload = await trendsRes.json();
        if (trendsPayload.status === "success") setTrends(trendsPayload.data);

        // Fetch Pipeline Module 2: Intent Demand Scoring Engine
        const demandRes = await fetch(
          "http://localhost:5000/api/demand-scores",
        );
        if (!demandRes.ok)
          throw new Error(
            `Demand API returned error status: ${demandRes.status}`,
          );
        const demandPayload = await demandRes.json();
        if (demandPayload.status === "success")
          setDemandScores(demandPayload.data);

        // Fetch Pipeline Module 3: Supply-Demand Mismatch Quadrant
        const mismatchRes = await fetch(
          "http://localhost:5000/api/supply-demand",
        );
        if (!mismatchRes.ok)
          throw new Error(
            `Mismatch API returned error status: ${mismatchRes.status}`,
          );
        const mismatchPayload = await mismatchRes.json();
        if (mismatchPayload.status === "success")
          setMismatchData(mismatchPayload.data);
      } catch (err: unknown) {
        console.error("Data engineering link layer error: ", err);
        setError(
          err instanceof Error
            ? err.message
            : "Failed to capture backend data streams.",
        );
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  // ==========================================
  // UNIFIED CROSS-MODULE SEARCH FILTER LOGIC
  // ==========================================
  const cleanQuery = searchQuery.trim().toLowerCase();

  const filteredTrends = trends.filter(
    (row) =>
      row.state.toLowerCase().includes(cleanQuery) ||
      row.category.toLowerCase().includes(cleanQuery),
  );

  const filteredDemand = demandScores.filter(
    (row) =>
      row.state.toLowerCase().includes(cleanQuery) ||
      row.product_name.toLowerCase().includes(cleanQuery) ||
      row.city.toLowerCase().includes(cleanQuery) ||
      row.category.toLowerCase().includes(cleanQuery),
  );

  const filteredMismatch = mismatchData.filter(
    (row) =>
      row.state.toLowerCase().includes(cleanQuery) ||
      row.product_name.toLowerCase().includes(cleanQuery) ||
      row.city.toLowerCase().includes(cleanQuery) ||
      row.status.toLowerCase().includes(cleanQuery),
  );

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased pb-12">
      {/* ==========================================
          TOP BRANDING NAVIGATION BANNER LAYER
         ========================================== */}
      <div className="bg-blue-900 text-white shadow-md mb-6">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight">
                Geo-Spatial E-Commerce Analytics Dashboard
              </h1>
              <p className="text-blue-200 mt-1 text-sm font-medium">
                Next.js Application Frontend ➔ Flask Preprocessing API Data
                Tunnel
              </p>
            </div>
            {/* Reactive Navigation Tab Switches */}
            <div className="flex bg-blue-950/60 p-1 rounded-lg border border-blue-800 gap-1 self-start md:self-auto">
              <button
                onClick={() => setActiveTab("regional-trends")}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${activeTab === "regional-trends" ? "bg-blue-600 text-white shadow" : "text-blue-300 hover:text-white"}`}
              >
                📍 Trends
              </button>
              <button
                onClick={() => setActiveTab("demand-scores")}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${activeTab === "demand-scores" ? "bg-blue-600 text-white shadow" : "text-blue-300 hover:text-white"}`}
              >
                📊 Demand
              </button>
              <button
                onClick={() => setActiveTab("supply-demand")}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${activeTab === "supply-demand" ? "bg-blue-600 text-white shadow" : "text-blue-300 hover:text-white"}`}
              >
                ⚖️ Stock Mismatch
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6">
        {/* ==========================================
            UNIFIED DYNAMIC SEARCH SEARCHBAR COMPONENT
           ========================================== */}
        {!loading && !error && (
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="w-full md:max-w-md">
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1.5 tracking-wider">
                🔍 Cross-Module Unified Search Engine
              </label>
              <input
                type="text"
                placeholder="Enter State name or Product catalog label (e.g. Telangana, Product Item 1225)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-gray-900 shadow-inner"
              />
            </div>
            {cleanQuery && (
              <div className="self-end md:self-auto text-xs font-medium text-blue-800 bg-blue-50 border border-blue-200 rounded-md px-3 py-1.5 shadow-sm">
                Filtering metrics by query:{" "}
                <span className="font-bold font-mono">
                  &quot;{searchQuery}&quot;
                </span>
              </div>
            )}
          </div>
        )}

        {/* ==========================================
            UNIFIED PROCESS RUNTIME STATE HANDLING
           ========================================== */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-gray-600 font-medium">
              Extracting Columnar Parquet File Vector Blocks...
            </p>
          </div>
        )}

        {error && (
          <div className="p-6 text-center text-red-700 bg-red-50 rounded-xl border border-red-200 shadow-inner max-w-xl mx-auto">
            <span className="text-2xl mr-2">⚠️</span>{" "}
            <strong>Connection Failure:</strong> {error}
            <p className="text-xs text-red-500 font-normal mt-2">
              Verify that your local Python Flask service is actively listening
              on port 5000 and the Spark analytics engines have written out the
              Parquet folders to your storage space.
            </p>
          </div>
        )}

        {/* ==========================================
            TAB CONTENT VISUALIZATION GRID BLOCKS
           ========================================== */}
        {!loading && !error && (
          <div className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200">
            {/* VIEW TAB 1: REGIONAL SALES TRENDS */}
            {activeTab === "regional-trends" && (
              <div>
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-blue-950">
                      Module 1: Regional Sales & Revenue Analysis
                    </h2>
                    <p className="text-xs text-gray-500">
                      Aggregated transaction volumes and total gross GMV
                      segmented by geographic state boundaries.
                    </p>
                  </div>
                  <span className="text-xs font-mono font-bold bg-blue-50 text-blue-800 px-2.5 py-1 rounded border border-blue-100 shadow-sm">
                    Showing {filteredTrends.length} records
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="bg-blue-950 text-white font-semibold uppercase text-xs">
                        <th className="p-4">State Hub</th>
                        <th className="p-4">Retail Category</th>
                        <th className="p-4 text-right">Orders Generated</th>
                        <th className="p-4 text-right">Gross GMV (₹)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredTrends.length === 0 ? (
                        <tr>
                          <td
                            colSpan={4}
                            className="p-8 text-center text-gray-400"
                          >
                            No matching regional trends metrics match your
                            search query layer.
                          </td>
                        </tr>
                      ) : (
                        filteredTrends.map((row, i) => (
                          <tr
                            key={i}
                            className="hover:bg-blue-50/20 transition-colors"
                          >
                            <td className="p-4 font-semibold text-gray-800">
                              {row.state}
                            </td>
                            <td className="p-4 text-gray-600">
                              {row.category}
                            </td>
                            <td className="p-4 text-right font-mono text-blue-800">
                              {row.total_orders.toLocaleString()}
                            </td>
                            <td className="p-4 text-right font-mono font-bold text-emerald-700">
                              ₹
                              {row.total_revenue.toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                              })}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* VIEW TAB 2: WEIGHTED DEMAND SCORING MATRIX */}
            {activeTab === "demand-scores" && (
              <div>
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-blue-950">
                      Module 2: Funnel-Weighted Regional Demand Scores
                    </h2>
                    <p className="text-xs text-gray-500">
                      Min-Max normalized intent score coefficients calculated
                      using custom funnel thresholds [0.15*Search + 0.20*View +
                      0.30*Cart + 0.35*Purchase].
                    </p>
                  </div>
                  <span className="text-xs font-mono font-bold bg-blue-50 text-blue-800 px-2.5 py-1 rounded border border-blue-100 shadow-sm whitespace-nowrap">
                    Showing {filteredDemand.length} records
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="bg-blue-950 text-white font-semibold uppercase text-xs">
                        <th className="p-4">State Region</th>
                        <th className="p-4">City Hub Target</th>
                        <th className="p-4">Product Catalog Label</th>
                        <th className="p-4">Category</th>
                        <th className="p-4 text-right">
                          Composite Demand Index
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredDemand.length === 0 ? (
                        <tr>
                          <td
                            colSpan={5}
                            className="p-8 text-center text-gray-400"
                          >
                            No matching demand intent scoring entries match your
                            search query layer.
                          </td>
                        </tr>
                      ) : (
                        filteredDemand.map((row, i) => (
                          <tr
                            key={i}
                            className="hover:bg-blue-50/20 transition-colors"
                          >
                            <td className="p-4 text-gray-700">{row.state}</td>
                            <td className="p-4 font-semibold text-gray-800">
                              {row.city}
                            </td>
                            <td className="p-4 text-gray-900 font-medium">
                              {row.product_name}
                            </td>
                            <td className="p-4 text-gray-500">
                              {row.category}
                            </td>
                            <td className="p-4 text-right">
                              <span className="font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 text-xs">
                                {row.demand_score.toFixed(4)}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* VIEW TAB 3: SUPPLY-DEMAND MISMATCH ENGINE */}
            {activeTab === "supply-demand" && (
              <div>
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-blue-950">
                      Module 3: Regional Stock Shortages &amp; Excess Surplus
                      Tracking
                    </h2>
                    <p className="text-xs text-gray-500">
                      Distributed relational join matching available local
                      warehouse item counts against computed customer demand
                      scoring limits.
                    </p>
                  </div>
                  <span className="text-xs font-mono font-bold bg-blue-50 text-blue-800 px-2.5 py-1 rounded border border-blue-100 shadow-sm whitespace-nowrap">
                    Showing {filteredMismatch.length} records
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="bg-blue-950 text-white font-semibold uppercase text-xs">
                        <th className="p-4">Region City</th>
                        <th className="p-4">Target Product Catalog Item</th>
                        <th className="p-4 text-right">
                          Available Warehouse Stock
                        </th>
                        <th className="p-4 text-right">Demand Intent</th>
                        <th className="p-4 text-right">
                          Stock-to-Demand (SDR)
                        </th>
                        <th className="p-4 text-center">
                          Operational Alert State
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredMismatch.length === 0 ? (
                        <tr>
                          <td
                            colSpan={6}
                            className="p-8 text-center text-gray-400"
                          >
                            No warehouse balance mismatch rows match your
                            current search parameters.
                          </td>
                        </tr>
                      ) : (
                        filteredMismatch.map((row, i) => (
                          <tr
                            key={i}
                            className="hover:bg-blue-50/20 transition-colors"
                          >
                            <td className="p-4 font-semibold text-gray-800">
                              {row.city}{" "}
                              <span className="text-xs text-gray-400 font-normal">
                                ({row.state})
                              </span>
                            </td>
                            <td className="p-4 text-gray-900 font-medium">
                              {row.product_name}
                            </td>
                            <td className="p-4 text-right font-mono font-semibold text-gray-700">
                              {row.available_stock.toLocaleString()}
                            </td>
                            <td className="p-4 text-right font-mono text-blue-600 text-xs">
                              {row.demand_score.toFixed(4)}
                            </td>
                            <td className="p-4 text-right font-mono font-bold text-gray-800">
                              {row.sdr.toFixed(4)}
                            </td>
                            <td className="p-4 text-center">
                              <span
                                className={`px-2.5 py-1 rounded text-xs font-bold shadow-sm border ${
                                  row.status === "CRITICAL_SHORTAGE"
                                    ? "bg-red-50 text-red-700 border-red-200 animate-pulse"
                                    : row.status === "EXCESS_INVENTORY"
                                      ? "bg-amber-50 text-amber-700 border-amber-200"
                                      : "bg-emerald-50 text-emerald-700 border-emerald-200"
                                }`}
                              >
                                {row.status.replaceAll("_", " ")}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

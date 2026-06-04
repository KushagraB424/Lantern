"use client";

import { useState } from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { Activity, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const initialNodes = [
  { id: "START", data: { label: "START" }, position: { x: 250, y: 50 }, type: 'input' },
  { id: "dataset_understanding", data: { label: "Dataset Understanding" }, position: { x: 250, y: 150 } },
  { id: "data_quality", data: { label: "Data Quality Review" }, position: { x: 250, y: 250 } },
  { id: "analysis_planning", data: { label: "Analysis Planning (Interrupt)" }, position: { x: 250, y: 350 }, style: { border: '2px solid #eab308' } },
  { id: "analysis_execution", data: { label: "Code Execution" }, position: { x: 250, y: 450 } },
  { id: "visualization", data: { label: "Visualization Generation" }, position: { x: 250, y: 550 } },
  { id: "insight_generation", data: { label: "Insight Generation" }, position: { x: 250, y: 650 } },
  { id: "recommendation_generation", data: { label: "Recommendation Generation" }, position: { x: 250, y: 750 } },
  { id: "report_generation", data: { label: "Report Generation" }, position: { x: 250, y: 850 } },
  { id: "END", data: { label: "END" }, position: { x: 250, y: 950 }, type: 'output' },
];

const initialEdges = [
  { id: "e-start-understanding", source: "START", target: "dataset_understanding", animated: true },
  { id: "e-understanding-quality", source: "dataset_understanding", target: "data_quality", animated: true },
  { id: "e-quality-planning", source: "data_quality", target: "analysis_planning", animated: true },
  { id: "e-planning-execution", source: "analysis_planning", target: "analysis_execution", animated: true },
  { id: "e-execution-viz", source: "analysis_execution", target: "visualization", animated: true },
  { id: "e-viz-insights", source: "visualization", target: "insight_generation", animated: true },
  { id: "e-insights-rec", source: "insight_generation", target: "recommendation_generation", animated: true },
  { id: "e-rec-report", source: "recommendation_generation", target: "report_generation", animated: true },
  { id: "e-report-end", source: "report_generation", target: "END", animated: true },
];

export default function ObservabilityPage() {
  const [threadId, setThreadId] = useState("");
  const [trace, setTrace] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  const handleTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!threadId) return;
    setIsSearching(true);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE}/api/observability/${threadId}/trace`);
      const data = await response.json();
      if (data.status === "success") {
        setTrace(data.trace);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Observability Dashboard</h1>
        <p className="text-muted-foreground">Monitor LangGraph execution paths and trace history.</p>
      </div>

      <form onSubmit={handleTrace} className="flex gap-4 max-w-xl">
        <Input 
          placeholder="Enter Thread ID to view historical trace..." 
          value={threadId}
          onChange={(e) => setThreadId(e.target.value)}
        />
        <Button type="submit" disabled={isSearching} className="gap-2">
          <Search className="h-4 w-4" /> Trace
        </Button>
      </form>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px]">
        {/* React Flow Graph */}
        <div className="lg:col-span-2 rounded-xl border bg-card overflow-hidden h-[600px] relative shadow-sm">
          <ReactFlow 
            nodes={initialNodes} 
            edges={initialEdges} 
            fitView
            className="bg-slate-50 dark:bg-slate-900"
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>

        {/* Trace Log */}
        <div className="rounded-xl border bg-card p-6 shadow-sm overflow-y-auto h-[600px] space-y-4">
          <h2 className="font-semibold text-lg flex items-center gap-2 border-b pb-2">
            <Activity className="h-5 w-5 text-primary" /> Execution Trace
          </h2>
          {trace.length > 0 ? (
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
              {trace.map((step, idx) => (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active mb-4">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full border border-white bg-slate-300 group-[.is-active]:bg-primary text-slate-500 group-[.is-active]:text-emerald-50 shadow-sm shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                    <span className="text-xs font-bold">{idx + 1}</span>
                  </div>
                  <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] bg-white dark:bg-muted p-3 rounded-lg border shadow-sm">
                    <div className="font-bold text-slate-900 dark:text-white text-sm mb-1">{step.node}</div>
                    <div className="text-xs text-slate-500">
                      {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : 'Unknown Time'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center p-8 border border-dashed rounded-lg text-muted-foreground mt-8">
              Enter a valid Thread ID to see the execution sequence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

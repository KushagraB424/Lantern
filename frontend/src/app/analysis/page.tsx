"use client";

import { useSearchParams } from "next/navigation";
import { useState, Suspense, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Play, Settings2, CheckCircle2, Edit3, Loader2, Code2, BarChart3, Terminal, FileText, Download } from "lucide-react";
import { PlotlyChart } from "@/components/ui/plotly-chart";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function AnalysisConfig() {
  const searchParams = useSearchParams();
  const datasetId = searchParams.get("dataset");

  const [provider, setProvider] = useState("google");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(2000);
  
  const [isStarting, setIsStarting] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  
  const [plan, setPlan] = useState("");
  const [qualityScore, setQualityScore] = useState(100);
  const [isResuming, setIsResuming] = useState(false);
  const [isEditingPlan, setIsEditingPlan] = useState(false);
  
  const [executionData, setExecutionData] = useState<any>(null);
  
  const reportRef = useRef<HTMLDivElement>(null);

  // Load state from local storage on mount
  useEffect(() => {
    if (!datasetId) return;
    const savedState = localStorage.getItem(`analysis_state_${datasetId}`);
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        if (parsed.threadId) setThreadId(parsed.threadId);
        if (parsed.plan) setPlan(parsed.plan);
        if (parsed.qualityScore) setQualityScore(parsed.qualityScore);
        if (parsed.executionData) setExecutionData(parsed.executionData);
      } catch (e) {
        console.error("Failed to parse local storage state", e);
      }
    }
  }, [datasetId]);

  // Save state to local storage when it changes
  useEffect(() => {
    if (!datasetId) return;
    localStorage.setItem(`analysis_state_${datasetId}`, JSON.stringify({
      threadId,
      plan,
      qualityScore,
      executionData
    }));
  }, [datasetId, threadId, plan, qualityScore, executionData]);

  if (!datasetId) {
    return (
      <div className="flex flex-col h-full gap-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Analysis</h1>
          <p className="text-muted-foreground">View your active and past data analyses.</p>
        </div>
        <div className="flex-1 rounded-xl border bg-card text-card-foreground shadow-sm flex items-center justify-center p-6">
          <p className="text-muted-foreground">No active analysis. Please upload a dataset first.</p>
        </div>
      </div>
    );
  }

  const handleStartAnalysis = async () => {
    setIsStarting(true);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE}/api/analysis/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: datasetId,
          settings: {
            provider,
            model_name: model,
            temperature,
            max_tokens: maxTokens
          }
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      
      if (data.status === "waiting_for_approval") {
        setThreadId(data.thread_id);
        setPlan(data.plan);
        setQualityScore(data.quality_score);
      }
    } catch (e: any) {
      alert("Error starting analysis: " + e.message);
    } finally {
      setIsStarting(false);
    }
  };

  const handleApprovePlan = async () => {
    if (!threadId) return;
    setIsResuming(true);
    
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE}/api/analysis/${threadId}/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "approve",
          updated_plan: plan
        })
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      
      setExecutionData(data);
      
      // Also save to history_reports array for the History page to use
      const historyReportsStr = localStorage.getItem("history_reports") || "[]";
      try {
        const historyReports = JSON.parse(historyReportsStr);
        // Avoid duplicate reports for same dataset
        const existingIdx = historyReports.findIndex((r: any) => r.dataset_id === datasetId);
        const newReport = {
          dataset_id: datasetId,
          summary: data.plan?.split('\n')[0] || "Analysis report",
          quality_score: qualityScore,
          report_text: data.final_report,
          timestamp: new Date().toISOString()
        };
        if (existingIdx !== -1) {
          historyReports[existingIdx] = newReport;
        } else {
          historyReports.unshift(newReport); // Add to beginning
        }
        localStorage.setItem("history_reports", JSON.stringify(historyReports));
      } catch (e) {
        console.error("Failed to update history reports in localStorage", e);
      }
    } catch (e: any) {
      alert("Error resuming: " + e.message);
    } finally {
      setIsResuming(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!executionData?.final_report) return;
    const blob = new Blob([executionData.final_report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Lantern_Report_${datasetId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const handleDownloadPDF = async () => {
    if (!reportRef.current) return;
    try {
      // @ts-ignore
      const html2pdf = (await import('html2pdf.js')).default;
      const opt = {
        margin:       10,
        filename:     `Lantern_Report_${datasetId}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      html2pdf().set(opt as any).from(reportRef.current).save();
    } catch (e) {
      console.error("PDF generation failed:", e);
      alert("Failed to generate PDF.");
    }
  };

  if (executionData) {
    return (
      <div className="flex flex-col h-full gap-8 max-w-7xl mx-auto w-full">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">Final Analysis Report</h1>
            <p className="text-muted-foreground">Generated autonomously by Lantern AI Agents.</p>
          </div>
          <div className="flex gap-4">
             <Button variant="outline" onClick={handleDownloadMarkdown} className="gap-2">
               <FileText className="h-4 w-4" /> Export Markdown
             </Button>
             <Button onClick={handleDownloadPDF} className="gap-2 font-bold">
               <Download className="h-4 w-4" /> Export PDF
             </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Column: The Report */}
          <div className="xl:col-span-2 rounded-xl border bg-card p-10 shadow-sm space-y-4" ref={reportRef}>
            <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {executionData.final_report || "Report generation failed."}
              </ReactMarkdown>
            </div>
            
            <div className="mt-12 space-y-8">
               <h3 className="text-2xl font-bold border-b pb-2">Interactive Visualizations</h3>
               {executionData.visualizations && executionData.visualizations.length > 0 ? (
                executionData.visualizations.map((chart: any, i: number) => (
                  <div key={i} className="h-[400px] border rounded-lg p-2 shadow-sm bg-white dark:bg-background">
                    <PlotlyChart data={chart.data} layout={chart.layout} />
                  </div>
                ))
               ) : (
                 <p className="text-muted-foreground">No visualizations available.</p>
               )}
            </div>
          </div>

          {/* Right Column: Code & Logs (hidden from PDF) */}
          <div className="space-y-8">
             <div className="space-y-4">
               <h2 className="text-xl font-semibold flex items-center gap-2">
                 <Code2 className="h-5 w-5 text-primary" />
                 Execution Code
               </h2>
               <pre className="bg-muted p-4 rounded-xl text-xs font-mono overflow-x-auto max-h-[500px] border">
                 {executionData.generated_code || "No code generated."}
               </pre>
             </div>

             <div className="space-y-4">
               <h2 className="text-xl font-semibold flex items-center gap-2">
                 <Terminal className="h-5 w-5 text-primary" />
                 Execution Logs
               </h2>
               <pre className="bg-black text-green-400 p-4 rounded-xl text-xs font-mono overflow-x-auto max-h-[300px] shadow-inner">
                 {executionData.execution_logs || "No logs available."}
               </pre>
             </div>
          </div>
        </div>
      </div>
    );
  }

  if (threadId) {
    return (
      <div className="flex flex-col h-full gap-6 max-w-4xl mx-auto w-full">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Review Analysis Plan</h1>
          <p className="text-muted-foreground">The AI has generated a plan based on the dataset summary and quality review.</p>
        </div>
        
        <div className="grid gap-6">
          <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-4 border-b">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Proposed Execution Plan
              </h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${qualityScore > 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                Data Quality Score: {qualityScore}/100
              </span>
            </div>
            
            {isEditingPlan ? (
              <textarea 
                className="w-full min-h-[300px] p-4 rounded-md border font-mono text-sm bg-background"
                value={plan}
                onChange={(e) => setPlan(e.target.value)}
              />
            ) : (
              <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {plan}
                </ReactMarkdown>
              </div>
            )}
            
            <div className="flex gap-4 pt-4 border-t">
              <Button 
                variant="outline" 
                onClick={() => setIsEditingPlan(!isEditingPlan)}
                className="gap-2"
                disabled={isResuming}
              >
                <Edit3 className="h-4 w-4" />
                {isEditingPlan ? "Preview Plan" : "Edit Plan"}
              </Button>
              <Button 
                onClick={handleApprovePlan} 
                className="gap-2 flex-1 font-bold"
                disabled={isResuming}
              >
                {isResuming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                {isResuming ? "Executing..." : "Approve & Execute Plan"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full gap-6 max-w-4xl mx-auto w-full">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Analysis Settings</h1>
        <p className="text-muted-foreground">Configure the AI agents before starting the workflow.</p>
      </div>
      
      <div className="grid gap-6">
        <div className="rounded-xl border bg-card p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-2 pb-4 border-b">
            <Settings2 className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Model Configuration</h2>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Model Selection</label>
              <select 
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                value={model}
                onChange={(e) => {
                  setModel(e.target.value);
                  setProvider(e.target.value.includes("gemini") ? "google" : "openrouter");
                }}
              >
                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                <option value="nvidia/nemotron-3-super-120b-a12b:free">Nemotron 3 Super (OpenRouter)</option>
              </select>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm font-medium">Temperature</label>
                <span className="text-sm text-muted-foreground">{temperature}</span>
              </div>
              <input 
                type="range" 
                min="0" max="1" step="0.1" 
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Max Tokens</label>
              <input 
                type="number" 
                value={Number.isNaN(maxTokens) ? "" : maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value) || 0)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
          </div>
          
          <div className="pt-6">
            <Button size="lg" className="w-full gap-2 font-bold" onClick={handleStartAnalysis} disabled={isStarting}>
              {isStarting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              {isStarting ? "Generating Plan..." : "Generate Analysis Plan"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AnalysisConfig />
    </Suspense>
  )
}

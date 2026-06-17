"use client";

import { useState } from "react";
import { Search, FileText, BarChart2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";

export default function HistoryPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setHasSearched(true);
    try {
      // First check local storage
      const historyReportsStr = localStorage.getItem("history_reports") || "[]";
      let localResults: any[] = [];
      try {
        const historyReports = JSON.parse(historyReportsStr);
        localResults = historyReports.filter((r: any) => 
          r.summary?.toLowerCase().includes(query.toLowerCase()) || 
          r.dataset_id?.toLowerCase().includes(query.toLowerCase()) ||
          r.report_text?.toLowerCase().includes(query.toLowerCase())
        ).map((r: any) => ({ ...r, similarity_score: 1.0 })); // Fake high score for local match
      } catch (e) {
        console.error("Failed to parse local history reports", e);
      }

      // Then check API
      let apiResults: any[] = [];
      try {
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (data.status === "success") {
          apiResults = data.results;
        }
      } catch (e) {
        console.error("API Search failed", e);
      }
      
      // Merge and deduplicate by dataset_id
      const combined = [...localResults, ...apiResults];
      const unique = combined.filter((v, i, a) => a.findIndex(t => t.dataset_id === v.dataset_id) === i);
      setResults(unique);
      
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex flex-col h-full gap-8 max-w-4xl mx-auto w-full">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Analysis History</h1>
        <p className="text-muted-foreground">Search past executive reports using natural language semantic search.</p>
      </div>
      
      <form onSubmit={handleSearch} className="flex gap-4">
        <Input 
          type="text" 
          placeholder="e.g., 'sales forecasting' or 'revenue decline'" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" disabled={isSearching} className="gap-2 font-bold">
          <Search className="h-4 w-4" />
          {isSearching ? "Searching..." : "Search"}
        </Button>
      </form>
      
      <div className="space-y-6">
        {results.length > 0 ? (
          results.map((result, i) => (
            <div 
              key={i} 
              className="rounded-xl border bg-card p-6 shadow-sm space-y-4 transition-all hover:border-primary cursor-pointer"
              onClick={() => setExpandedId(expandedId === i ? null : i)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    Dataset: {result.dataset_id}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{result.summary}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${result.quality_score > 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    Quality: {result.quality_score}
                  </span>
                  <span className="text-xs text-muted-foreground">Match Score: {(1 - result.similarity_score).toFixed(2)}</span>
                </div>
              </div>
              
              <div className="bg-muted p-4 rounded-md">
                <p className="text-xs font-mono text-muted-foreground mb-2 flex items-center gap-1">
                  <BarChart2 className="h-3 w-3" /> Report Preview
                </p>
                <div className={`text-sm relative transition-all duration-300 ${expandedId === i ? 'h-auto' : 'h-32 overflow-hidden'}`}>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{result.report_text}</ReactMarkdown>
                  </div>
                  {expandedId !== i && (
                    <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-muted to-transparent"></div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          !isSearching && hasSearched && (
            <div className="text-center p-12 border border-dashed rounded-xl text-muted-foreground">
              No previous analyses found matching your query.
            </div>
          )
        )}
      </div>
    </div>
  );
}

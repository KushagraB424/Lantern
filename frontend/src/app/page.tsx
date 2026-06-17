"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { UploadCloud, Loader2 } from "lucide-react";

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".csv") && !file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      setError("Please upload a valid CSV or Excel file.");
      return;
    }

    setError(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      console.log("Upload success:", data.metadata);
      
      localStorage.setItem("last_dataset_id", data.metadata.dataset_id);
      
      router.push(`/analysis?dataset=${data.metadata.dataset_id}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An unexpected error occurred during upload.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] items-center justify-center max-w-3xl mx-auto text-center gap-10 animate-in fade-in zoom-in duration-500">
      <div className="space-y-4">
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
          Understand your data in seconds
        </h1>
        <p className="text-xl text-muted-foreground">
          Upload a dataset and let Lantern analyze, visualize, and extract insights automatically. No SQL or Python required.
        </p>
      </div>

      <div 
        className="w-full max-w-xl border-2 border-dashed border-border rounded-xl p-12 bg-card flex flex-col items-center justify-center gap-4 hover:border-primary/50 transition-colors cursor-pointer group"
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden" 
          accept=".csv,.xlsx,.xls"
        />
        <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:scale-110 transition-transform">
          {isUploading ? (
            <Loader2 className="h-8 w-8 text-primary animate-spin" />
          ) : (
            <UploadCloud className="h-8 w-8 text-primary" />
          )}
        </div>
        <div className="space-y-1">
          <p className="text-lg font-medium">
            {isUploading ? "Uploading & Analyzing..." : "Click to upload or drag and drop"}
          </p>
          <p className="text-sm text-muted-foreground">CSV or Excel files up to 50MB</p>
        </div>
        
        {error && (
          <p className="text-destructive text-sm mt-2">{error}</p>
        )}

        <Button className="mt-4" size="lg" disabled={isUploading}>
          {isUploading ? "Processing..." : "Select File"}
        </Button>
      </div>
    </div>
  );
}

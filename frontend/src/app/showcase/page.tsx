import { Sparkles, BarChart2, CheckCircle2, FileText, Code2, Terminal } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { PlotlyChart } from "@/components/ui/plotly-chart";

const showcaseData = {
  final_report: `
# Executive Data Analysis Report

## 1. Executive Summary
This report analyzes global E-commerce sales data, identifying key seasonal trends and underperforming regions. 

## 2. Dataset Overview
The dataset contains 50,000 records of online transactions across 12 countries.

## 3. Data Quality Findings
**Quality Score: 95/100**
- 50 missing values in 'Discount' column (Imputed with 0)
- No duplicate records detected.

## 4. Analysis Plan
1. Clean missing values in critical columns.
2. Aggregate revenue by Region.
3. Calculate month-over-month growth patterns.

## 5. Key Insights
- **Europe** accounts for 45% of total revenue.
- Q4 shows a 120% spike in sales compared to Q3.
- Electronics category yields the highest margin (35%), while apparel lags at 12%.

## 6. Recommendations
- **Increase ad spend** in Europe during Q3 to capture early holiday demand.
- **Investigate** shipping bottlenecks in South America which correlate with higher refund rates.
- **Expand** electronics inventory ahead of next quarter.
`,
  generated_code: "import pandas as pd\nimport json\n\ndf = pd.read_csv(DATASET_PATH)\n# Aggregation logic\nresult = {'tables': {'revenue': [{'Region': 'Europe', 'Rev': 45000}]}}\nprint(json.dumps(result))",
  execution_logs: "Process completed successfully in 1.2 seconds.",
  visualizations: [
    {
      data: [{
        x: ['North America', 'Europe', 'Asia', 'South America', 'Africa'],
        y: [30000, 45000, 20000, 5000, 0],
        type: 'bar',
        marker: { color: '#3b82f6' }
      }],
      layout: {
        title: 'Revenue by Region',
        xaxis: { title: 'Region' },
        yaxis: { title: 'Revenue (USD)' }
      }
    }
  ]
};

export default function ShowcasePage() {
  return (
    <div className="flex flex-col h-full gap-8 max-w-7xl mx-auto w-full pb-20">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-yellow-500" />
          Showcase Mode
        </h1>
        <p className="text-muted-foreground">Demo Lantern's capabilities instantly with pre-computed analysis samples. Perfect for interviews and presentations.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 rounded-xl border bg-card p-10 shadow-sm space-y-4">
          <h2 className="text-xl font-bold border-b pb-2 mb-4 flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-500" />
            Sample: E-commerce Global Sales
          </h2>
          <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {showcaseData.final_report}
            </ReactMarkdown>
          </div>
          
          <div className="mt-12 space-y-8">
             <h3 className="text-2xl font-bold border-b pb-2">Interactive Visualizations (Demo)</h3>
             {showcaseData.visualizations.map((chart: any, i: number) => (
               <div key={i} className="h-[400px] border rounded-lg p-2 shadow-sm bg-white dark:bg-background">
                 <PlotlyChart data={chart.data} layout={chart.layout} />
               </div>
             ))}
          </div>
        </div>

        <div className="space-y-8">
           <div className="space-y-4">
             <h2 className="text-xl font-semibold flex items-center gap-2 border-b pb-2">
               <Code2 className="h-5 w-5 text-primary" />
               Execution Code Trace
             </h2>
             <pre className="bg-muted p-4 rounded-xl text-xs font-mono overflow-x-auto border shadow-sm">
               {showcaseData.generated_code}
             </pre>
           </div>
           <div className="space-y-4">
             <h2 className="text-xl font-semibold flex items-center gap-2 border-b pb-2">
               <Terminal className="h-5 w-5 text-primary" />
               Sandbox Execution Logs
             </h2>
             <pre className="bg-black text-green-400 p-4 rounded-xl text-xs font-mono overflow-x-auto shadow-inner">
               {showcaseData.execution_logs}
             </pre>
           </div>
        </div>
      </div>
    </div>
  );
}

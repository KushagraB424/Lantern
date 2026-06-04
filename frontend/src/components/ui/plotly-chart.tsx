"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { 
  ssr: false, 
  loading: () => <div className="h-[400px] w-full animate-pulse bg-muted rounded-xl flex items-center justify-center text-muted-foreground">Loading Chart...</div> 
});

export function PlotlyChart({ data, layout }: { data: any, layout: any }) {
  return (
    <Plot
      data={data}
      layout={{ 
        ...layout, 
        autosize: true, 
        paper_bgcolor: 'transparent', 
        plot_bgcolor: 'transparent', 
        font: { color: '#888888' } 
      }}
      useResizeHandler
      style={{ width: '100%', height: '100%' }}
      config={{ responsive: true, displayModeBar: false }}
    />
  );
}

export default function VisualizationsPage() {
  return (
    <div className="flex flex-col h-full gap-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Visualizations</h1>
        <p className="text-muted-foreground">Interactive charts and graphs generated from your data.</p>
      </div>
      <div className="flex-1 rounded-xl border bg-card text-card-foreground shadow-sm flex items-center justify-center p-6">
        <p className="text-muted-foreground">Upload a dataset and run an analysis to generate visualizations.</p>
      </div>
    </div>
  )
}

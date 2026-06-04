import Link from 'next/link';
import { Home, BarChart2, History, Activity, Sparkles } from 'lucide-react';

const navItems = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Analysis', href: '/analysis', icon: BarChart2 },
  { name: 'History', href: '/history', icon: History },
  { name: 'Showcase', href: '/showcase', icon: Sparkles },
  { name: 'Observability', href: '/observability', icon: Activity },
];

export function Sidebar() {
  return (
    <div className="w-64 border-r bg-card flex flex-col h-full shadow-sm relative z-10">
      <div className="h-14 flex items-center px-4 font-bold text-lg border-b bg-background gap-2">
        <Sparkles className="h-5 w-5 text-primary" />
        Lantern AI
      </div>
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-accent hover:text-accent-foreground text-sm font-medium transition-colors"
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t text-xs text-muted-foreground text-center">
        v1.0.0
      </div>
    </div>
  );
}

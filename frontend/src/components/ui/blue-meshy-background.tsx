import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function BlueMeshyBackground({ className, children }: { className?: string; children?: ReactNode }) {
  return (
    <div className={cn("relative min-h-screen w-full overflow-hidden bg-slate-950 text-slate-50", className)}>
      <div className="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] bg-[radial-gradient(ellipse_at_center,rgba(14,165,233,0.15),transparent_40%)] animate-[spin_60s_linear_infinite]" />
      <div className="absolute top-0 right-0 w-[100%] h-[100%] bg-[radial-gradient(circle_at_80%_20%,rgba(56,189,248,0.1),transparent_50%)]" />
      <div className="relative z-10 w-full h-full flex flex-col">
        {children}
      </div>
    </div>
  );
}

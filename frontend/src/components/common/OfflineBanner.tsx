import React from 'react';
import { Wifi, WifiOff, ShieldCheck, Zap } from 'lucide-react';

interface OfflineBannerProps {
  isOnline: boolean;
  queuedActionsCount?: number;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  isOnline,
  queuedActionsCount = 0
}) => {
  if (isOnline && queuedActionsCount === 0) {
    return (
      <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
        <Wifi className="w-3.5 h-3.5 animate-pulse" />
        <span>CQRS LIVE (<span className="text-emerald-300">18ms</span>)</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-300 text-xs font-mono shadow-[0_0_15px_rgba(255,183,3,0.2)] animate-pulse">
      <WifiOff className="w-4 h-4 text-amber-400" />
      <span>STADIUM 5G RESILIENT MODE {queuedActionsCount > 0 && `(${queuedActionsCount} QUEUED)`}</span>
      <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
    </div>
  );
};

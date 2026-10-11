import React from 'react';

interface GlowingBadgeProps {
  variant?: 'cyan' | 'purple' | 'ember' | 'gold' | 'green' | 'blue';
  children: React.ReactNode;
  icon?: React.ReactNode;
  pulsing?: boolean;
  className?: string;
}

export const GlowingBadge: React.FC<GlowingBadgeProps> = ({
  variant = 'cyan',
  children,
  icon,
  pulsing = false,
  className = ''
}) => {
  const variantStyles = {
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 shadow-[0_0_12px_rgba(0,240,255,0.2)]',
    purple: 'bg-purple-500/10 text-purple-300 border-purple-500/30 shadow-[0_0_12px_rgba(157,78,221,0.2)]',
    ember: 'bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-[0_0_12px_rgba(255,0,85,0.2)]',
    gold: 'bg-amber-500/10 text-amber-300 border-amber-500/30 shadow-[0_0_12px_rgba(255,183,3,0.2)]',
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_12px_rgba(0,255,136,0.2)]',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/30 shadow-[0_0_12px_rgba(58,134,255,0.2)]'
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold tracking-wider font-display border backdrop-blur-md ${variantStyles[variant]} ${className}`}
    >
      {pulsing && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${variant === 'ember' ? 'bg-rose-400' : 'bg-cyan-400'}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${variant === 'ember' ? 'bg-rose-500' : 'bg-cyan-500'}`} />
        </span>
      )}
      {icon && <span className="opacity-90">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};

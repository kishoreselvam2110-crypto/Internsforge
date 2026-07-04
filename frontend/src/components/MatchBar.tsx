import React from 'react';

interface MatchBarProps {
  label: string;
  score: number; // 0 to 100
  colorClass: string;
  maxPoints?: number; // purely visual for the rubric feel
}

export function MatchBar({ label, score, colorClass, maxPoints = 100 }: MatchBarProps) {
  // Determine if it's a perfect score for a special annotation
  const isPerfect = score >= 99;
  
  return (
    <div className="mb-4">
      <div className="flex justify-between items-end mb-1">
        <span className="font-sans text-sm font-medium text-foreground">{label}</span>
        <span className="monospace-score text-sm text-foreground/80">
          {score.toFixed(0)}/{maxPoints}
        </span>
      </div>
      
      <div className="w-full h-3 bg-muted rounded-full overflow-hidden relative">
        <div 
          className={`h-full ${colorClass} transition-all duration-1000 ease-out`}
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>
      {isPerfect && (
        <div className="annotation text-sm mt-1 float-right clear-both text-success">
          Perfect!
        </div>
      )}
    </div>
  );
}

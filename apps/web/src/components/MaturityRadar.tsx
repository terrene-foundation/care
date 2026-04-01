"use client";

import { useEffect, useRef } from "react";

interface Dimension {
  name: string;
  score: number;
}

interface MaturityRadarProps {
  dimensions: Dimension[];
  size?: number;
}

/**
 * SVG-based radar chart for CARE maturity scores.
 * No D3 dependency — pure SVG for simplicity.
 */
export function MaturityRadar({ dimensions, size = 240 }: MaturityRadarProps) {
  const center = size / 2;
  const radius = (size - 40) / 2;
  const maxScore = 5;
  const levels = [1, 2, 3, 4, 5];

  if (dimensions.length === 0) return null;

  const angleStep = (2 * Math.PI) / dimensions.length;

  const getPoint = (index: number, value: number) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = (value / maxScore) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Build the score polygon path
  const scorePath =
    dimensions
      .map((d, i) => {
        const p = getPoint(i, d.score);
        return `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`;
      })
      .join(" ") + " Z";

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Grid levels */}
        {levels.map((level) => {
          const points = dimensions
            .map((_, i) => {
              const p = getPoint(i, level);
              return `${p.x},${p.y}`;
            })
            .join(" ");
          return (
            <polygon
              key={level}
              points={points}
              fill="none"
              stroke="var(--care-border)"
              strokeWidth={level === maxScore ? 1.5 : 0.5}
              opacity={0.6}
            />
          );
        })}

        {/* Axis lines */}
        {dimensions.map((_, i) => {
          const p = getPoint(i, maxScore);
          return (
            <line
              key={`axis-${i}`}
              x1={center}
              y1={center}
              x2={p.x}
              y2={p.y}
              stroke="var(--care-border)"
              strokeWidth={0.5}
              opacity={0.4}
            />
          );
        })}

        {/* Score polygon */}
        <path
          d={scorePath}
          fill="var(--care-accent)"
          fillOpacity={0.2}
          stroke="var(--care-accent)"
          strokeWidth={2}
        />

        {/* Score dots */}
        {dimensions.map((d, i) => {
          const p = getPoint(i, d.score);
          return (
            <circle
              key={`dot-${i}`}
              cx={p.x}
              cy={p.y}
              r={4}
              fill="var(--care-accent)"
            />
          );
        })}

        {/* Labels */}
        {dimensions.map((d, i) => {
          const labelRadius = radius + 18;
          const angle = angleStep * i - Math.PI / 2;
          const x = center + labelRadius * Math.cos(angle);
          const y = center + labelRadius * Math.sin(angle);
          return (
            <text
              key={`label-${i}`}
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="var(--care-text-secondary)"
              fontSize={10}
              fontWeight={500}
            >
              {d.name}
            </text>
          );
        })}
      </svg>

      {/* Score legend */}
      <div className="flex flex-wrap gap-3 mt-2 justify-center">
        {dimensions.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs">
            <div
              className="w-2 h-2 rounded-full"
              style={{ background: "var(--care-accent)" }}
            />
            <span style={{ color: "var(--care-text-secondary)" }}>
              {d.name}: {d.score.toFixed(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

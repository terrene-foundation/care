// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/**
 * DmSkeleton -- loading placeholder for the DM Team dashboard.
 *
 * Mimics the layout of the full DM dashboard: summary stats row,
 * agent cards grid, and task submission form.
 */

"use client";

import Skeleton from "../../../components/ui/Skeleton";

/** Full-page skeleton for the DM Team dashboard. */
export default function DmSkeleton() {
  return (
    <div className="space-y-6">
      {/* Summary stats row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <Skeleton className="mb-2 h-3 w-20" />
            <Skeleton className="h-7 w-14" />
          </div>
        ))}
      </div>

      {/* Agent cards grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 bg-white p-5"
          >
            <div className="mb-3 flex items-start justify-between">
              <div>
                <Skeleton className="mb-2 h-4 w-32" />
                <Skeleton className="h-3 w-48" />
              </div>
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-24 rounded-full" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
        ))}
      </div>

      {/* Task submission form skeleton */}
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <Skeleton className="mb-4 h-5 w-40" />
        <Skeleton className="mb-3 h-20 w-full" />
        <div className="flex gap-3">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
    </div>
  );
}

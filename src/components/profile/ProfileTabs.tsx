"use client";

import { useState } from "react";

interface ProfileTab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface ProfileTabsProps {
  tabs: ProfileTab[];
}

export function ProfileTabs({ tabs }: ProfileTabsProps) {
  const [activeId, setActiveId] = useState(tabs[0]?.id ?? "");

  return (
    <div>
      <div className="mx-auto max-w-[1400px] px-4 pt-6 lg:px-8">
        <div className="flex gap-6 border-b border-divider">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveId(tab.id)}
              className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${activeId === tab.id
                ? "border-accent text-accent"
                : "border-transparent text-text-secondary hover:text-text-primary"
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      {tabs.find((t) => t.id === activeId)?.content}
    </div>
  );
}
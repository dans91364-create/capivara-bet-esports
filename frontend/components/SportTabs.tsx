"use client";

interface SportTabsProps {
  sports: string[];
  selectedSport: string;
  onSelectSport: (sport: string) => void;
}

const sportColors: Record<string, string> = {
  valorant: "border-red-500 text-red-400",
  cs2: "border-orange-500 text-orange-400",
  lol: "border-blue-500 text-blue-400",
  dota2: "border-red-700 text-red-400",
  nba: "border-purple-500 text-purple-400",
};

const sportLabels: Record<string, string> = {
  valorant: "Valorant",
  cs2: "CS2",
  lol: "League of Legends",
  dota2: "Dota 2",
  nba: "NBA",
};

export default function SportTabs({ sports, selectedSport, onSelectSport }: SportTabsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {sports.map((sport) => {
        const isSelected = selectedSport === sport;
        const colorClass = sportColors[sport] || "border-slate-500 text-slate-400";
        
        return (
          <button
            key={sport}
            onClick={() => onSelectSport(sport)}
            className={`
              px-6 py-3 rounded-lg font-semibold transition-all whitespace-nowrap
              ${isSelected 
                ? `bg-slate-700 border-2 ${colorClass}` 
                : "bg-slate-800 border-2 border-slate-700 text-slate-400 hover:bg-slate-700 hover:border-slate-600"
              }
            `}
          >
            {sportLabels[sport] || sport.toUpperCase()}
          </button>
        );
      })}
    </div>
  );
}

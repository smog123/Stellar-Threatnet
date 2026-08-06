import { timeAgo } from "@/lib/time";

export interface ActivityItem {
  kind: "report" | "incident" | "threat";
  id: string;
  title: string;
  detail: string;
  badge: string;
  badgeClass: string;
  time: string;
}

const KIND_ICON: Record<ActivityItem["kind"], string> = {
  report: "📩",
  incident: "🚨",
  threat: "⚠️",
};

export default function ActivityFeed({ items }: { items: ActivityItem[] }) {
  if (items.length === 0) {
    return <p className="py-6 text-center text-sm text-slate-500">No recent activity.</p>;
  }
  return (
    <ul className="divide-y divide-threat-border/60">
      {items.map((item) => (
        <li key={item.id} className="flex items-start gap-3 py-3">
          <span className="mt-0.5 text-base">{KIND_ICON[item.kind]}</span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-200">{item.title}</p>
            <p className="truncate text-xs text-slate-500">{item.detail}</p>
          </div>
          <div className="flex shrink-0 flex-col items-end gap-1">
            <span className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${item.badgeClass}`}>
              {item.badge}
            </span>
            <span className="text-[11px] text-slate-500">{timeAgo(item.time)}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}

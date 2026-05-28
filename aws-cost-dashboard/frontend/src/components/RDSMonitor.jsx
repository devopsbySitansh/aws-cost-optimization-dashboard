// RDSMonitor.jsx
export function RDSMonitor({ instances }) {
  const underutilized = instances.filter((i) =>
    ["CRITICALLY_UNDERUTILIZED", "UNDERUTILIZED"].includes(i.utilization_status)
  ).length;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium flex items-center gap-2">
          <span className="text-blue-400">▪</span> RDS Instances
        </h2>
        {underutilized > 0 && (
          <span className="text-[11px] px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full">
            {underutilized} underutilized
          </span>
        )}
      </div>
      <div className="space-y-2">
        {instances.map((db) => (
          <div key={db.db_instance_id} className="flex items-center gap-3 px-3 py-2 bg-gray-800/50 rounded-lg">
            <div className="w-7 h-7 bg-blue-500/10 rounded-md flex items-center justify-center text-blue-400 text-xs flex-shrink-0">
              ⬡
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{db.db_instance_id}</p>
              <p className="text-[11px] text-gray-500">{db.db_class} · {db.engine}</p>
            </div>
            <div className="text-right">
              <p className={`text-xs font-medium ${db.avg_cpu_7d < 20 ? "text-red-400" : "text-green-400"}`}>
                {db.avg_cpu_7d.toFixed(1)}% CPU
              </p>
              <p className="text-[10px] text-gray-500">{db.avg_connections_7d.toFixed(0)} connections</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// AlertsPanel.jsx
export function AlertsPanel({ alerts }) {
  const alarms = alerts?.alarms ?? [];
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium">🔔 CloudWatch Alarms</h2>
        <span className={`text-[11px] px-2 py-0.5 rounded-full border ${
          alarms.length > 0
            ? "bg-red-500/10 text-red-400 border-red-500/20"
            : "bg-green-500/10 text-green-400 border-green-500/20"
        }`}>
          {alarms.length > 0 ? `${alarms.length} ALARM` : "All OK"}
        </span>
      </div>
      {alarms.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">✓ No active alarms</p>
      ) : (
        <div className="space-y-2">
          {alarms.map((alarm, i) => (
            <div key={i} className="px-3 py-2.5 bg-red-500/5 border border-red-500/15 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse" />
                <p className="text-xs font-medium text-red-300">{alarm.name}</p>
              </div>
              <p className="text-[11px] text-gray-500">{alarm.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// CostBreakdown.jsx
export function CostBreakdown({ costSummary }) {
  const breakdown = costSummary?.breakdown ?? [];
  const total = costSummary?.total_cost_usd ?? 0;
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium">💰 Cost Breakdown</h2>
        <span className="text-xs text-gray-400">{costSummary?.period_start} → {costSummary?.period_end}</span>
      </div>
      <div className="space-y-2">
        {breakdown.slice(0, 6).map((item) => (
          <div key={item.service} className="flex items-center gap-2">
            <div className="flex-1 text-xs text-gray-300 truncate">{item.service}</div>
            <div className="w-24 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500 rounded-full"
                style={{ width: `${Math.round((item.cost_usd / total) * 100)}%` }}
              />
            </div>
            <div className="text-xs font-medium w-14 text-right">${item.cost_usd.toFixed(2)}</div>
          </div>
        ))}
        <div className="pt-2 border-t border-gray-800 flex justify-between text-xs">
          <span className="text-gray-500">Total this month</span>
          <span className="font-medium text-orange-400">${total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}

export default RDSMonitor;

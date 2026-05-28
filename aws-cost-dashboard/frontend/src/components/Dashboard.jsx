import EC2Monitor from "./EC2Monitor";
import RDSMonitor from "./RDSMonitor";
import CostRecommendations from "./CostRecommendations";
import AlertsPanel from "./AlertsPanel";
import CostBreakdown from "./CostBreakdown";

export default function Dashboard({ data, demoMode }) {
  const totalSavings = data?.recommendations?.total_potential_savings ?? 0;
  const monthlyTotal = data?.cost_summary?.total_cost_usd ?? 0;
  const ec2Count = data?.ec2?.count ?? 0;
  const rdsCount = data?.rds?.count ?? 0;
  const alarmCount = data?.alerts?.count ?? 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top Bar */}
      <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">☁</div>
          <div>
            <h1 className="text-sm font-medium">AWS Cost Optimization Dashboard</h1>
            <p className="text-xs text-gray-500">ap-south-1 · Account: 123456789012</p>
          </div>
          {demoMode && (
            <span className="text-xs px-2 py-0.5 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full">
              Demo Mode
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse inline-block" />
          Live · Updated 2m ago
        </div>
      </header>

      <main className="px-6 py-5 max-w-7xl mx-auto">
        {/* KPI Strip */}
        <div className="grid grid-cols-4 gap-3 mb-6">
          {[
            { label: "EC2 Instances", value: ec2Count, sub: "Running & stopped", color: "text-orange-400" },
            { label: "RDS Instances", value: rdsCount, sub: "All available", color: "text-blue-400" },
            { label: "This Month", value: `$${monthlyTotal.toFixed(2)}`, sub: "Total AWS spend", color: "text-yellow-400" },
            { label: "Potential Savings", value: `$${totalSavings.toFixed(2)}`, sub: "If recommendations applied", color: "text-green-400" },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-xs text-gray-500 mb-1">{kpi.label}</p>
              <p className={`text-2xl font-medium ${kpi.color}`}>{kpi.value}</p>
              <p className="text-xs text-gray-600 mt-0.5">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {alarmCount > 0 && (
          <div className="mb-5 px-4 py-3 bg-red-500/5 border border-red-500/20 rounded-xl flex items-center gap-3 text-sm">
            <span className="text-red-400">⚠</span>
            <span className="text-gray-300">
              <strong className="text-red-400">{alarmCount} active alarm{alarmCount > 1 ? "s" : ""}:</strong>{" "}
              {data.alerts.alarms[0]?.description}
            </span>
          </div>
        )}

        {/* Main grid */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <EC2Monitor instances={data.ec2?.instances ?? []} />
          <RDSMonitor instances={data.rds?.instances ?? []} />
        </div>

        <CostRecommendations recommendations={data.recommendations} />

        <div className="grid grid-cols-2 gap-4 mt-4">
          <CostBreakdown costSummary={data.cost_summary} />
          <AlertsPanel alerts={data.alerts} />
        </div>
      </main>
    </div>
  );
}

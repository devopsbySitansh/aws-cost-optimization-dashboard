export default function CostRecommendations({ recommendations }) {
  const recs = recommendations?.recommendations ?? [];
  const total = recommendations?.total_potential_savings ?? 0;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3 pb-3 border-b border-gray-800">
        <h2 className="text-sm font-medium flex items-center gap-2">
          <span className="text-orange-400">💡</span> Cost Optimization Recommendations
        </h2>
        <span className="text-sm">
          Total potential saving:{" "}
          <strong className="text-green-400">${total.toFixed(2)} / month</strong>
        </span>
      </div>
      <div className="space-y-2">
        {recs.map((rec, idx) => (
          <div key={idx} className="flex items-center gap-3 px-3 py-2.5 bg-gray-800/40 rounded-lg">
            <span
              className={`text-[10px] font-medium px-2 py-0.5 rounded min-w-[40px] text-center border ${
                rec.priority === "HIGH"
                  ? "bg-red-500/10 text-red-400 border-red-500/20"
                  : "bg-orange-500/10 text-orange-400 border-orange-500/20"
              }`}
            >
              {rec.priority}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium">{rec.name || rec.resource_id} ({rec.current_type})</p>
              <p className="text-[11px] text-gray-500">→ {rec.recommendation} — avg CPU {rec.avg_cpu_7d}%</p>
            </div>
            <span className="text-sm font-medium text-green-400 whitespace-nowrap">
              ${rec.estimated_monthly_saving.toFixed(2)}/mo
            </span>
          </div>
        ))}
        {recs.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            ✓ No recommendations — all resources look appropriately sized.
          </p>
        )}
      </div>
    </div>
  );
}

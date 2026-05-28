const STATUS_CONFIG = {
  CRITICALLY_UNDERUTILIZED: { label: "Critical", cls: "bg-red-500/10 text-red-400 border-red-500/20" },
  UNDERUTILIZED:            { label: "Low CPU", cls: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  NORMAL:                   { label: "Normal",  cls: "bg-green-500/10 text-green-400 border-green-500/20" },
  HIGH:                     { label: "High",    cls: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
};

function CpuBar({ pct }) {
  const color = pct < 10 ? "bg-red-500" : pct < 20 ? "bg-orange-500" : pct > 80 ? "bg-yellow-400" : "bg-green-500";
  return (
    <div className="w-20">
      <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="text-right text-[10px] text-gray-500 mt-0.5">{pct.toFixed(1)}%</p>
    </div>
  );
}

export default function EC2Monitor({ instances }) {
  const underutilized = instances.filter((i) =>
    ["CRITICALLY_UNDERUTILIZED", "UNDERUTILIZED"].includes(i.status)
  ).length;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium flex items-center gap-2">
          <span className="text-orange-400">▪</span> EC2 Instances
        </h2>
        {underutilized > 0 && (
          <span className="text-[11px] px-2 py-0.5 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full">
            {underutilized} underutilized
          </span>
        )}
      </div>
      <div className="space-y-2">
        {instances.map((inst) => {
          const status = STATUS_CONFIG[inst.status] ?? STATUS_CONFIG.NORMAL;
          return (
            <div key={inst.instance_id} className="flex items-center gap-3 px-3 py-2 bg-gray-800/50 rounded-lg">
              <div className="w-7 h-7 bg-orange-500/10 rounded-md flex items-center justify-center text-orange-400 text-xs flex-shrink-0">
                ⬡
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate">{inst.name || inst.instance_id}</p>
                <p className="text-[11px] text-gray-500">{inst.instance_type}</p>
              </div>
              <CpuBar pct={inst.avg_cpu_7d} />
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${status.cls}`}>
                {status.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

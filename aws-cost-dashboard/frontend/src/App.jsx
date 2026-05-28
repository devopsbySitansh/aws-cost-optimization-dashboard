import { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard";
import sampleData from "../public/sample_data.json";

// Toggle DEMO_MODE = true to run without a real AWS backend
const DEMO_MODE = true;
const API_BASE = "http://localhost:5000/api";

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchAll() {
      try {
        if (DEMO_MODE) {
          // Simulate network delay for realism
          await new Promise((r) => setTimeout(r, 800));
          setData(sampleData);
        } else {
          const [ec2, rds, recs, cost, alerts] = await Promise.all([
            fetch(`${API_BASE}/ec2/metrics`).then((r) => r.json()),
            fetch(`${API_BASE}/rds/metrics`).then((r) => r.json()),
            fetch(`${API_BASE}/recommendations`).then((r) => r.json()),
            fetch(`${API_BASE}/cost/summary`).then((r) => r.json()),
            fetch(`${API_BASE}/alerts`).then((r) => r.json()),
          ]);
          setData({ ec2, rds, recommendations: recs, cost_summary: cost, alerts });
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Fetching CloudWatch metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center text-red-400">
          <p className="text-lg font-medium mb-2">Failed to load dashboard</p>
          <p className="text-sm text-gray-500">{error}</p>
          <p className="text-xs text-gray-600 mt-3">Check your AWS credentials and Flask backend.</p>
        </div>
      </div>
    );
  }

  return <Dashboard data={data} demoMode={DEMO_MODE} />;
}

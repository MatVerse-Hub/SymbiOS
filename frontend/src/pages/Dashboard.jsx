import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [newDecision, setNewDecision] = useState({
    title: '',
    context: '',
    human_confidence: 0.75,
    risk_tolerance: 0.5
  });
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (token) {
      loadMetrics();
      loadHistory();
    }
  }, [token]);

  const loadMetrics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/metrics/omega`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMetrics(response.data);
      setUser(response.data.user_omega_score);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/metrics/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(response.data.history);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const submitDecision = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/decisions`, newDecision, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`✅ Decision created! Ω-Score: ${response.data.omega_score}`);
      setNewDecision({ title: '', context: '', human_confidence: 0.75, risk_tolerance: 0.5 });
      loadMetrics();
      loadHistory();
    } catch (error) {
      console.error('Error submitting decision:', error);
      alert('❌ Error submitting decision');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">🧬 SymbiOS Dashboard</h1>
        <p className="text-slate-400">Córtex-Exocórtex Symbiotic Decision Engine</p>
      </header>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-emerald-900 to-emerald-800 p-6 rounded-lg">
            <p className="text-slate-300 mb-2">Ω-Score</p>
            <p className="text-4xl font-bold">{metrics.user_omega_score.toFixed(3)}</p>
            <p className="text-sm text-emerald-300 mt-2">
              {metrics.user_omega_score > 0.85 ? '✅ Antifrágil' : '⚠️ Borderline'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-lg">
            <p className="text-slate-300 mb-2">Avg Ω</p>
            <p className="text-4xl font-bold">{metrics.decisions_omega_avg.toFixed(3)}</p>
            <p className="text-sm text-blue-300 mt-2">{metrics.decisions_count} decisions</p>
          </div>

          <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-6 rounded-lg">
            <p className="text-slate-300 mb-2">Recommendations</p>
            <p className="text-2xl font-bold">{metrics.recommendations.ACCELERATE} 🚀</p>
            <p className="text-sm text-purple-300 mt-2">{metrics.recommendations.MONITOR} 🔔 {metrics.recommendations.PAUSE} ⏸️</p>
          </div>

          <div className="bg-gradient-to-br from-amber-900 to-amber-800 p-6 rounded-lg">
            <p className="text-slate-300 mb-2">Status</p>
            <p className="text-2xl font-bold">{metrics.antifragile}</p>
            <p className="text-sm text-amber-300 mt-2">System Health</p>
          </div>
        </div>
      )}

      {/* New Decision Form */}
      <div className="bg-slate-800 p-6 rounded-lg mb-8">
        <h2 className="text-2xl font-bold mb-4">📝 Submit Decision for Calibration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Decision title"
            value={newDecision.title}
            onChange={(e) => setNewDecision({...newDecision, title: e.target.value})}
            className="bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
          />
          <textarea
            placeholder="Context / reasoning"
            value={newDecision.context}
            onChange={(e) => setNewDecision({...newDecision, context: e.target.value})}
            className="bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
          />
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm mb-2">Human Confidence: {newDecision.human_confidence.toFixed(2)}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={newDecision.human_confidence}
              onChange={(e) => setNewDecision({...newDecision, human_confidence: parseFloat(e.target.value)})}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Risk Tolerance: {newDecision.risk_tolerance.toFixed(2)}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={newDecision.risk_tolerance}
              onChange={(e) => setNewDecision({...newDecision, risk_tolerance: parseFloat(e.target.value)})}
              className="w-full"
            />
          </div>
        </div>
        <button
          onClick={submitDecision}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-700 px-6 py-2 rounded font-bold disabled:opacity-50"
        >
          {loading ? 'Processing...' : '✅ Calibrate Decision'}
        </button>
      </div>

      {/* Charts */}
      {history.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Ω-Score Over Time */}
          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-4">Ω-Score Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history}>
                <CartesianGrid stroke="#475569" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{backgroundColor: '#1e293b'}} />
                <Legend />
                <Line type="monotone" dataKey="omega_score" stroke="#10b981" name="Ω-Score" dot={{fill: '#10b981'}} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* CVaR-95 Distribution */}
          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-4">Risk Profile (CVaR-95)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={history}>
                <CartesianGrid stroke="#475569" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{backgroundColor: '#1e293b'}} />
                <Bar dataKey="cvar_95" fill="#f59e0b" name="CVaR-95" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="text-center text-slate-400 mt-12">
        <p>🔗 Blockchain: Polygon Amoy | 🧠 AI: NumPy + Monte Carlo | 🔐 Audit Trail: Immutable</p>
      </footer>
    </div>
  );
}

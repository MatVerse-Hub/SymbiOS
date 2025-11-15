import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    organization: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup';
      const response = await axios.post(`${API_URL}${endpoint}`, form);

      localStorage.setItem('token', response.data.token);
      window.location.href = '/dashboard';
    } catch (error) {
      alert(`❌ Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-lg p-8 shadow-xl">
        <h1 className="text-3xl font-bold text-white mb-2">🧬 SymbiOS</h1>
        <p className="text-slate-400 mb-8">Córtex-Exocórtex Symbiosis</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({...form, email: e.target.value})}
            required
            className="w-full bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({...form, password: e.target.value})}
            required
            className="w-full bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
          />

          {!isLogin && (
            <>
              <input
                type="text"
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm({...form, name: e.target.value})}
                className="w-full bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
              />
              <input
                type="text"
                placeholder="Organization"
                value={form.organization}
                onChange={(e) => setForm({...form, organization: e.target.value})}
                className="w-full bg-slate-700 px-4 py-2 rounded text-white placeholder-slate-400"
              />
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Loading...' : isLogin ? 'Login' : 'Sign Up'}
          </button>
        </form>

        <button
          onClick={() => setIsLogin(!isLogin)}
          className="w-full mt-4 text-slate-400 hover:text-white"
        >
          {isLogin ? 'Need an account? Sign Up' : 'Already have an account? Login'}
        </button>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function useAuth() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const login = (t) => { localStorage.setItem("token", t); setToken(t); };
  const logout = () => { localStorage.removeItem("token"); setToken(null); };
  return { token, login, logout };
}

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(API + "/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      onLogin(data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ background: "#1e293b", borderRadius: "1rem", padding: "2rem", width: "100%", maxWidth: "400px", boxShadow: "0 25px 50px rgba(0,0,0,0.5)" }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{ fontSize: "3rem" }}>🏒</div>
          <h1 style={{ color: "white", fontSize: "1.8rem", fontWeight: "bold", margin: "0.5rem 0 0.25rem" }}>Coach Dashboard</h1>
          <p style={{ color: "#94a3b8", margin: 0 }}>Hockey Analytics Platform</p>
        </div>
        {error && <div style={{ background: "#450a0a", color: "#fca5a5", padding: "0.75rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.9rem" }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ color: "#cbd5e1", display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
              style={{ width: "100%", background: "#334155", color: "white", border: "1px solid #475569", borderRadius: "0.5rem", padding: "0.75rem", fontSize: "1rem", boxSizing: "border-box" }}
              placeholder="coach@team.com" />
          </div>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ color: "#cbd5e1", display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
              style={{ width: "100%", background: "#334155", color: "white", border: "1px solid #475569", borderRadius: "0.5rem", padding: "0.75rem", fontSize: "1rem", boxSizing: "border-box" }}
              placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading}
            style={{ width: "100%", background: loading ? "#1d4ed8" : "#2563eb", color: "white", border: "none", borderRadius: "0.75rem", padding: "0.9rem", fontSize: "1.1rem", fontWeight: "bold", cursor: loading ? "not-allowed" : "pointer" }}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Dashboard({ token, onLogout }) {
  const [games, setGames] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeGame, setActiveGame] = useState(null);
  const [tab, setTab] = useState("games");
  const navigate = useNavigate();

  useEffect(() => {
    fetch(API + "/api/v1/games", { headers: { Authorization: "Bearer " + token } })
      .then(r => r.json()).then(setGames).catch(console.error).finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    if (!activeGame) return;
    const wsUrl = (process.env.REACT_APP_WS_URL || "ws://localhost:8000") + "/api/v1/ws/game/" + activeGame.id + "?role=coach";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "alert") setAlerts(prev => [msg.data, ...prev].slice(0, 50));
      } catch {}
    };
    return () => ws.close();
  }, [activeGame]);

  const handleLogout = () => { onLogout(); navigate("/login"); };

  const TYPE_COLOR = { shot: "#ea580c", goal: "#16a34a", pressure: "#ca8a04" };
  const TYPE_ICON = { shot: "🎯", goal: "🥅", pressure: "⚡" };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ background: "#1e293b", padding: "1rem 1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #334155" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.5rem" }}>🏒</span>
          <span style={{ color: "white", fontWeight: "bold", fontSize: "1.2rem" }}>Coach Dashboard</span>
        </div>
        <button onClick={handleLogout} style={{ background: "none", border: "1px solid #475569", color: "#94a3b8", padding: "0.4rem 1rem", borderRadius: "0.5rem", cursor: "pointer" }}>
          Sign Out
        </button>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", padding: "1rem 1.5rem", borderBottom: "1px solid #1e293b" }}>
        {["games", "alerts"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "0.5rem 1.5rem", borderRadius: "0.5rem", border: "none", fontWeight: "bold", cursor: "pointer", background: tab === t ? "#2563eb" : "#1e293b", color: tab === t ? "white" : "#94a3b8", textTransform: "capitalize" }}>
            {t === "games" ? "🎮 Games" : "🚨 Alerts " + (alerts.length > 0 ? "(" + alerts.length + ")" : "")}
          </button>
        ))}
      </div>

      <div style={{ padding: "1.5rem", maxWidth: "800px", margin: "0 auto" }}>
        {tab === "games" && (
          <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h2 style={{ color: "white", margin: 0 }}>Games</h2>
              <a href={API + "/docs"} target="_blank" rel="noreferrer"
                style={{ background: "#2563eb", color: "white", padding: "0.5rem 1rem", borderRadius: "0.5rem", textDecoration: "none", fontSize: "0.9rem", fontWeight: "bold" }}>
                + Create Game via API
              </a>
            </div>
            {loading && <p style={{ color: "#94a3b8" }}>Loading games...</p>}
            {!loading && games.length === 0 && (
              <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🏒</div>
                <p style={{ marginBottom: "1rem" }}>No games yet.</p>
                <a href={API + "/docs#/games/create_game_api_v1_games_post"} target="_blank" rel="noreferrer"
                  style={{ color: "#3b82f6" }}>Create your first game in API Docs →</a>
              </div>
            )}
            {games.map(game => (
              <div key={game.id} onClick={() => setActiveGame(game)}
                style={{ background: activeGame?.id === game.id ? "#1e3a5f" : "#1e293b", borderRadius: "1rem", padding: "1.25rem", marginBottom: "0.75rem", cursor: "pointer", border: activeGame?.id === game.id ? "2px solid #3b82f6" : "2px solid transparent" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                  <div>
                    <h3 style={{ color: "white", margin: "0 0 0.25rem", fontWeight: "bold" }}>{game.name}</h3>
                    <p style={{ color: "#94a3b8", margin: 0, fontSize: "0.9rem" }}>{game.home_team} vs {game.away_team}</p>
                  </div>
                  <span style={{ background: game.status === "live" ? "#16a34a" : "#475569", color: "white", padding: "0.2rem 0.75rem", borderRadius: "9999px", fontSize: "0.8rem", fontWeight: "bold" }}>
                    {game.status === "live" ? "● LIVE" : game.status}
                  </span>
                </div>
                <div style={{ display: "flex", gap: "1.5rem", color: "#94a3b8", fontSize: "0.9rem" }}>
                  <span>Score: {game.home_score} - {game.away_score}</span>
                  <span>🎯 {game.total_shots} shots</span>
                  {activeGame?.id === game.id && <span style={{ color: "#3b82f6", fontWeight: "bold" }}>● Selected</span>}
                </div>
              </div>
            ))}
          </>
        )}

        {tab === "alerts" && (
          <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h2 style={{ color: "white", margin: 0 }}>
                Live Alerts {activeGame ? "- " + activeGame.name : ""}
              </h2>
              {alerts.length > 0 && (
                <button onClick={() => setAlerts([])} style={{ background: "none", border: "1px solid #475569", color: "#94a3b8", padding: "0.3rem 0.75rem", borderRadius: "0.5rem", cursor: "pointer", fontSize: "0.85rem" }}>
                  Clear
                </button>
              )}
            </div>
            {!activeGame && <p style={{ color: "#94a3b8" }}>Select a game from the Games tab to receive live alerts.</p>}
            {activeGame && alerts.length === 0 && <p style={{ color: "#64748b", textAlign: "center", padding: "3rem 0" }}>No alerts yet. Waiting for events...</p>}
            {alerts.map((alert, i) => (
              <div key={i} style={{ background: "#1e293b", borderLeft: "4px solid " + (TYPE_COLOR[alert.event_type] || "#3b82f6"), borderRadius: "0.75rem", padding: "1rem", marginBottom: "0.75rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontSize: "1.5rem" }}>{TYPE_ICON[alert.event_type] || "📍"}</span>
                  <div>
                    <p style={{ color: "white", fontWeight: "bold", margin: "0 0 0.25rem", textTransform: "capitalize" }}>{alert.event_type}!</p>
                    <p style={{ color: "#94a3b8", margin: 0, fontSize: "0.85rem" }}>
                      {alert.game_clock} · Confidence: {Math.round((alert.confidence || 0) * 100)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const { token, login, logout } = useAuth();
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <Login onLogin={login} />} />
        <Route path="/dashboard" element={token ? <Dashboard token={token} onLogout={logout} /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to={token ? "/dashboard" : "/login"} />} />
      </Routes>
    </BrowserRouter>
  );
}
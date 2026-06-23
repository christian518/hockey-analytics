import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useParams } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function GameList() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(API + "/api/v1/games")
      .then(r => r.json()).then(setGames).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ background: "linear-gradient(to bottom, #1e3a5f, #0f172a)", padding: "3rem 1rem 2rem", textAlign: "center" }}>
        <div style={{ fontSize: "3.5rem", marginBottom: "0.5rem" }}>🏒</div>
        <h1 style={{ color: "white", fontSize: "2rem", fontWeight: "900", margin: "0 0 0.5rem" }}>Hockey Highlights</h1>
        <p style={{ color: "#93c5fd", margin: 0 }}>Tournament Clips and Moments</p>
      </div>
      {loading && <p style={{ textAlign: "center", color: "#94a3b8", padding: "2rem" }}>Loading games...</p>}
      <div style={{ padding: "1rem", maxWidth: "500px", margin: "0 auto" }}>
        {games.map(game => (
          <button key={game.id} onClick={() => navigate("/game/" + game.id)}
            style={{ width: "100%", background: "#1e293b", border: "none", borderRadius: "1rem", padding: "1.25rem", marginBottom: "0.75rem", color: "white", textAlign: "left", cursor: "pointer", boxShadow: "0 4px 6px rgba(0,0,0,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              <p style={{ fontWeight: "bold", fontSize: "1.1rem", margin: 0 }}>{game.name}</p>
              <span style={{ background: game.status === "live" ? "#dc2626" : "#475569", color: "white", padding: "0.2rem 0.6rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: "bold" }}>
                {game.status === "live" ? "● LIVE" : game.status}
              </span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-around", marginBottom: "0.75rem" }}>
              <div style={{ textAlign: "center" }}>
                <p style={{ fontSize: "2.5rem", fontWeight: "900", margin: 0 }}>{game.home_score}</p>
                <p style={{ color: "#94a3b8", fontSize: "0.85rem", margin: 0 }}>{game.home_team}</p>
              </div>
              <div style={{ color: "#475569", fontWeight: "bold", alignSelf: "center", fontSize: "1.2rem" }}>VS</div>
              <div style={{ textAlign: "center" }}>
                <p style={{ fontSize: "2.5rem", fontWeight: "900", margin: 0 }}>{game.away_score}</p>
                <p style={{ color: "#94a3b8", fontSize: "0.85rem", margin: 0 }}>{game.away_team}</p>
              </div>
            </div>
            <p style={{ color: "#3b82f6", fontSize: "0.9rem", fontWeight: "bold", margin: 0 }}>View Highlights →</p>
          </button>
        ))}
        {!loading && games.length === 0 && (
          <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🏒</div>
            <p>No games available yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

function GamePage() {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const [game, setGame] = useState(null);
  const [clips, setClips] = useState([]);
  const [summary, setSummary] = useState(null);
  const [tab, setTab] = useState("highlights");

  useEffect(() => {
    Promise.all([
      fetch(API + "/api/v1/games/" + gameId).then(r => r.json()),
      fetch(API + "/api/v1/clips/game/" + gameId).then(r => r.json()),
      fetch(API + "/api/v1/games/" + gameId + "/summary").then(r => r.json()),
    ]).then(([g, c, s]) => { setGame(g); setClips(Array.isArray(c) ? c : []); setSummary(s); }).catch(console.error);
  }, [gameId]);

  if (!game) return (
    <div style={{ minHeight: "100vh", background: "#0f172a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "white", fontSize: "1.2rem" }}>Loading...</p>
    </div>
  );

  const TYPE_COLOR = { shot: "#ea580c", goal: "#16a34a", pressure: "#ca8a04", compilation: "#9333ea" };
  const TYPE_ICON = { shot: "🎯", goal: "🥅", pressure: "⚡", compilation: "🏆" };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", fontFamily: "system-ui, sans-serif", paddingBottom: "4rem" }}>
      <div style={{ position: "sticky", top: 0, zIndex: 20, background: "rgba(15,23,42,0.97)", borderBottom: "1px solid #1e293b", padding: "0.75rem 1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
          <button onClick={() => navigate("/")} style={{ background: "none", border: "none", color: "#3b82f6", fontSize: "1.3rem", cursor: "pointer", padding: 0 }}>←</button>
          <div style={{ flex: 1 }}>
            <p style={{ color: "white", fontWeight: "bold", margin: "0 0 0.1rem", fontSize: "1rem" }}>{game.name}</p>
            <p style={{ color: "#94a3b8", fontSize: "0.85rem", margin: 0 }}>{game.home_team} {game.home_score}–{game.away_score} {game.away_team}</p>
          </div>
          {game.status === "live" && <span style={{ background: "#dc2626", color: "white", fontSize: "0.7rem", fontWeight: "bold", padding: "0.2rem 0.5rem", borderRadius: "9999px" }}>LIVE</span>}
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {["highlights", "summary"].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ flex: 1, padding: "0.5rem", borderRadius: "0.75rem", border: "none", fontWeight: "bold", fontSize: "0.9rem", cursor: "pointer", background: tab === t ? "#2563eb" : "transparent", color: tab === t ? "white" : "#94a3b8" }}>
              {t === "highlights" ? "🎬 Highlights" : "📊 Summary"}
            </button>
          ))}
        </div>
      </div>

      {tab === "highlights" && (
        <div style={{ padding: "0.75rem", maxWidth: "500px", margin: "0 auto" }}>
          {clips.length === 0 && (
            <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
              <div style={{ fontSize: "3rem" }}>🎬</div>
              <p style={{ marginTop: "1rem" }}>No highlights yet</p>
            </div>
          )}
          {clips.map(clip => (
            <div key={clip.id} style={{ background: "#1e293b", borderRadius: "1rem", overflow: "hidden", marginBottom: "0.75rem" }}>
              {clip.clip_url ? (
                <video src={clip.clip_url} poster={clip.thumbnail_url} controls playsInline style={{ width: "100%", display: "block" }} />
              ) : (
                <div style={{ aspectRatio: "16/9", background: "#334155", display: "flex", alignItems: "center", justifyContent: "center", color: "#64748b", flexDirection: "column", gap: "0.5rem" }}>
                  <div style={{ fontSize: "2rem" }}>{clip.is_locked ? "🔒" : "⏳"}</div>
                  <p style={{ margin: 0, fontSize: "0.9rem" }}>{clip.is_locked ? "Locked" : "Generating..."}</p>
                </div>
              )}
              <div style={{ padding: "0.75rem" }}>
                <span style={{ background: TYPE_COLOR[clip.clip_type] || "#2563eb", color: "white", fontSize: "0.75rem", fontWeight: "bold", padding: "0.2rem 0.6rem", borderRadius: "9999px" }}>
                  {TYPE_ICON[clip.clip_type] || "🎬"} {clip.title}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "summary" && summary && (
        <div style={{ padding: "1rem", maxWidth: "500px", margin: "0 auto" }}>
          <div style={{ background: "linear-gradient(135deg, #1e3a5f, #1e293b)", borderRadius: "1rem", padding: "1.5rem", marginBottom: "1rem", textAlign: "center" }}>
            <p style={{ color: "#93c5fd", fontSize: "0.85rem", margin: "0 0 0.75rem", fontWeight: "bold", letterSpacing: "0.05em" }}>FINAL SCORE</p>
            <div style={{ display: "flex", justifyContent: "space-around", alignItems: "center" }}>
              <div>
                <p style={{ color: "white", fontSize: "3rem", fontWeight: "900", margin: 0 }}>{summary.home_score}</p>
                <p style={{ color: "#94a3b8", margin: 0 }}>{summary.home_team}</p>
              </div>
              <div style={{ color: "#475569", fontSize: "1.5rem", fontWeight: "bold" }}>–</div>
              <div>
                <p style={{ color: "white", fontSize: "3rem", fontWeight: "900", margin: 0 }}>{summary.away_score}</p>
                <p style={{ color: "#94a3b8", margin: 0 }}>{summary.away_team}</p>
              </div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            {[["🎯", "Shots", summary.total_shots || 0], ["🥅", "Goals", summary.event_counts?.goal || 0], ["⚡", "Pressure", summary.event_counts?.pressure || 0], ["🎬", "Highlights", summary.total_highlights || 0]].map(([icon, label, value]) => (
              <div key={label} style={{ background: "#1e293b", borderRadius: "1rem", padding: "1rem", textAlign: "center" }}>
                <div style={{ fontSize: "1.5rem" }}>{icon}</div>
                <div style={{ color: "white", fontSize: "2rem", fontWeight: "900", margin: "0.25rem 0" }}>{value}</div>
                <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<GameList />} />
        <Route path="/game/:gameId" element={<GamePage />} />
        <Route path="*" element={<GameList />} />
      </Routes>
    </BrowserRouter>
  );
}
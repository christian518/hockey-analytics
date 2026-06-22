import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useStore } from './store/useStore';

function ProtectedRoute({ children }) {
  const token = useStore((s) => s.token);
  return token ? children : <Navigate to="/login" replace />;
}

function Login() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const setAuth = useStore((s) => s.setAuth);
  const navigate = require('react-router-dom').useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      setAuth(data.access_token, { id: data.user_id, name: data.name, role: data.role });
      navigate('/dashboard');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
      <div style={{ background: '#1e293b', borderRadius: '1rem', padding: '2rem', width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '3rem' }}>??</div>
          <h1 style={{ color: 'white', fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.5rem' }}>Coach Dashboard</h1>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ color: '#94a3b8', display: 'block', marginBottom: '0.5rem' }}>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              style={{ width: '100%', background: '#334155', color: 'white', border: '1px solid #475569', borderRadius: '0.5rem', padding: '0.75rem', fontSize: '1rem' }}
              placeholder="coach@team.com" required />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ color: '#94a3b8', display: 'block', marginBottom: '0.5rem' }}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              style={{ width: '100%', background: '#334155', color: 'white', border: '1px solid #475569', borderRadius: '0.5rem', padding: '0.75rem', fontSize: '1rem' }}
              placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading}
            style={{ width: '100%', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.75rem', padding: '1rem', fontSize: '1.1rem', fontWeight: 'bold', cursor: 'pointer' }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

function Dashboard() {
  const { user, logout } = useStore();
  const navigate = require('react-router-dom').useNavigate();
  const [games, setGames] = React.useState([]);
  const [alerts, setAlerts] = React.useState([]);
  const token = useStore((s) => s.token);

  React.useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/games`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()).then(setGames).catch(console.error);
  }, [token]);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: 'white' }}>
      <div style={{ background: '#1e293b', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>??</span>
          <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>Coach Dashboard</span>
        </div>
        <button onClick={handleLogout} style={{ background: 'none', border: '1px solid #475569', color: '#94a3b8', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}>
          Sign Out
        </button>
      </div>
      <div style={{ padding: '1.5rem', maxWidth: '800px', margin: '0 auto' }}>
        <h2 style={{ marginBottom: '1rem', color: '#94a3b8' }}>Games</h2>
        {games.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>??</div>
            <p>No games yet. Use the API docs to create your first game.</p>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
              style={{ color: '#3b82f6', marginTop: '1rem', display: 'inline-block' }}>
              Open API Docs ?
            </a>
          </div>
        ) : (
          games.map(game => (
            <div key={game.id} style={{ background: '#1e293b', borderRadius: '1rem', padding: '1.25rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{game.name}</h3>
                  <p style={{ color: '#94a3b8', marginTop: '0.25rem' }}>{game.home_team} vs {game.away_team}</p>
                </div>
                <span style={{ background: game.status === 'live' ? '#16a34a' : '#475569', color: 'white', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                  {game.status}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.75rem', color: '#94a3b8', fontSize: '0.9rem' }}>
                <span>?? {game.total_shots} shots</span>
                <span>Score: {game.home_score} - {game.away_score}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

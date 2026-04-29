import { useState, useEffect } from 'react';
import { api } from './api/client';
import AuthScreen from './screens/AuthScreen';
import Spinner from './components/Spinner';

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('makanai_token') || '');
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  // On first load, if we have a token, verify it's still valid by calling /auth/me
  useEffect(() => {
    if (!token) {
      setChecking(false);
      return;
    }
    api.get('/auth/me', token)
      .then(me => {
        setUser(me);
        setChecking(false);
      })
      .catch(() => {
        // token expired or invalid → clear it
        localStorage.removeItem('makanai_token');
        setToken('');
        setChecking(false);
      });
  }, []); // empty deps = run once on mount

  const onAuth = (tok, me) => {
    setToken(tok);
    setUser(me);
  };

  const onLogout = () => {
    localStorage.removeItem('makanai_token');
    setToken('');
    setUser(null);
  };

  if (checking) {
    return (
      <div style={{ height:'100vh', display:'flex', alignItems:'center', justifyContent:'center', flexDirection:'column', gap:16 }}>
        <Spinner size={40} />
        <div style={{ fontFamily:'Lora', fontStyle:'italic', color:'var(--ink-lt)' }}>
          Loading makanai...
        </div>
      </div>
    );
  }

  if (!token || !user) {
    return <AuthScreen onAuth={onAuth} />;
  }

  // Logged in — placeholder home for now. We'll build AppShell next session.
  return (
    <div style={{ padding:40, textAlign:'center' }}>
      <h1 style={{ fontFamily:'Lora', fontStyle:'italic' }}>
        Welcome, {user.full_name || user.email} 🥥
      </h1>
      <p style={{ marginTop:12, color:'var(--ink-lt)' }}>
        Auth works! Sidebar + meal logging coming next session.
      </p>
      <button className="btn" onClick={onLogout} style={{ marginTop:20 }}>
        Sign out
      </button>
    </div>
  );
}
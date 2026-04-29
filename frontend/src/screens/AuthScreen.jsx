import { useState } from 'react';
import { api } from '../api/client';
import Spinner from '../components/Spinner';

export default function AuthScreen({ onAuth }) {
  const [mode, setMode] = useState('login');           // 'login' | 'register'
  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [registerSuccess, setRegisterSuccess] = useState(false);

  const set = (key, value) => {
    setForm(f => ({ ...f, [key]: value }));
    setError('');
  };

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setRegisterSuccess(false);

    try {
      if (mode === 'register') {
        await api.post('/auth/register', {
          email: form.email,
          password: form.password,
          full_name: form.full_name || undefined,
        });
        setMode('login');
        setRegisterSuccess(true);
        setForm(f => ({ ...f, password: '' }));
        return;
      }

      // login
      const data = await api.post('/auth/login', {
        email: form.email,
        password: form.password,
      });
      localStorage.setItem('makanai_token', data.access_token);
      const me = await api.get('/auth/me', data.access_token);
      onAuth(data.access_token, me);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: 'var(--cream)',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* decorative blobs */}
      <div style={{ position:'absolute', top:'-10%', right:'-8%', width:360, height:320, borderRadius:'60% 40%', background:'#EDE1C5', opacity:0.7 }}/>
      <div style={{ position:'absolute', bottom:'-8%', left:'-6%', width:300, height:280, borderRadius:'45% 55%', background:'#D4E8D0', opacity:0.5 }}/>

      <div className="fadeUp" style={{ width:'100%', maxWidth:420, position:'relative', zIndex:2 }}>
        {/* logo */}
        <div style={{ textAlign:'center', marginBottom:32 }}>
          <div style={{ fontFamily:'Lora', fontStyle:'italic', fontWeight:700, fontSize:38, color:'var(--ink)' }}>
            makanai
          </div>
          <div style={{ fontFamily:'Nunito', fontSize:13, color:'var(--ink-lt)', fontWeight:600, marginTop:4 }}>
            Your cosy calorie companion 🥥
          </div>
        </div>

        <div className="card" style={{ padding:'32px 36px' }}>
          {/* tabs */}
          <div style={{ display:'flex', marginBottom:24, border:'var(--border)', borderRadius:8, overflow:'hidden', background:'var(--cream2)' }}>
            {['login','register'].map(m => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(''); setRegisterSuccess(false); }}
                style={{
                  flex:1, padding:'10px', border:'none', cursor:'pointer',
                  background: mode === m ? 'var(--cream3)' : 'transparent',
                  fontWeight:800, fontSize:13,
                  color: mode === m ? 'var(--terra)' : 'var(--ink-mid)',
                  textTransform:'capitalize',
                  borderBottom: mode === m ? '2px solid var(--terra)' : '2px solid transparent',
                  transition:'all 0.2s',
                }}
              >
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          <form onSubmit={submit} style={{ display:'flex', flexDirection:'column', gap:14 }}>
            {mode === 'register' && (
              <div>
                <label style={{ display:'block', fontSize:12, fontWeight:800, color:'var(--ink-mid)', marginBottom:5 }}>Full Name</label>
                <input
                  className="input-field" type="text" placeholder="Aina Syahira"
                  value={form.full_name}
                  onChange={e => set('full_name', e.target.value)}
                />
              </div>
            )}

            <div>
              <label style={{ display:'block', fontSize:12, fontWeight:800, color:'var(--ink-mid)', marginBottom:5 }}>Email</label>
              <input
                className="input-field" type="email" placeholder="you@email.com"
                value={form.email}
                onChange={e => set('email', e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display:'block', fontSize:12, fontWeight:800, color:'var(--ink-mid)', marginBottom:5 }}>Password</label>
              <input
                className="input-field" type="password" placeholder="••••••••"
                value={form.password}
                onChange={e => set('password', e.target.value)}
                required
              />
            </div>

            {error && (
              <div style={{ background:'#FDE8E0', border:'1px solid var(--terra)', borderRadius:8, padding:'10px 14px', fontSize:13, color:'var(--terra)', fontWeight:600 }}>
                ⚠ {error}
              </div>
            )}

            {mode === 'login' && registerSuccess && (
              <div style={{ background:'#F0F8F0', border:'1px solid var(--sage)', borderRadius:8, padding:'10px 14px', fontSize:13, color:'var(--sage)', fontWeight:600 }}>
                ✓ Account created! Sign in below.
              </div>
            )}

            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading}
              style={{ marginTop:4, padding:'12px', fontSize:15 }}
            >
              {loading && <Spinner size={18} color="white" />}
              {loading ? 'Please wait...' : mode === 'login' ? 'Sign In 🍛' : 'Create Account ✨'}
            </button>
          </form>

          <div style={{ textAlign:'center', marginTop:18, fontSize:12, color:'var(--ink-lt)', fontWeight:600 }}>
            Backend: <code style={{ background:'var(--cream2)', padding:'2px 6px', borderRadius:4, fontSize:11 }}>http://localhost:8000</code>
          </div>
        </div>
      </div>
    </div>
  );
}
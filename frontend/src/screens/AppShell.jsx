// layout that wraps the logged-in app, the sidebar on the right, and a way to switch between them 

import { useState } from 'react';
import LogScreen from '../components/LogScreen';
import InsightsScreen from './InsightsScreen';
import HistoryScreen from './HistoryScreen';
import ChatScreen from './ChatScreen';

const NAV_ITEMS = [
  { id: 'log',      label: 'Log Meal', icon: '🍛' },
  { id: 'history',  label: 'History',  icon: '📖' },
  { id: 'chat',     label: 'AI Chat',  icon: '💬' },
  { id: 'insights', label: 'Insights', icon: '📊' },
];

export default function AppShell({ token, user, onLogout }) {
  const [tab, setTab] = useState('log');   // controling which tab is active

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* ─── SIDEBAR ─── */}
      <div style={{
        width: 220,
        background: 'var(--cream2)',
        borderRight: 'var(--border)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}>
        {/* logo */}
        <div style={{ padding: '22px 20px 18px', borderBottom: 'var(--border)' }}>
          <div style={{
            fontFamily: 'Lora',
            fontStyle: 'italic',
            fontWeight: 700,
            fontSize: 24,
            color: 'var(--ink)',
          }}>
            makanai
          </div>
          <div style={{
            fontSize: 11,
            fontWeight: 700,
            color: 'var(--ink-lt)',
            marginTop: 2,
          }}>
            Eat with Intention 🥥
          </div>
        </div>

        {/* user chip */}
        <div style={{
          padding: '14px 16px',
          borderBottom: 'var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          <div style={{
            width: 32, height: 32,
            borderRadius: '50%',
            background: 'var(--cream3)',
            border: 'var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            flexShrink: 0,
          }}>
            {(user?.full_name || user?.email || '?')[0].toUpperCase()}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <div style={{
              fontSize: 12,
              fontWeight: 800,
              color: 'var(--ink)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {user?.full_name || 'User'}
            </div>
            <div style={{
              fontSize: 10,
              fontWeight: 600,
              color: 'var(--ink-lt)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {user?.email}
            </div>
          </div>
        </div>

        {/* nav */}
        <nav style={{ flex: 1, padding: '14px 10px', display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '11px 14px',
                borderRadius: 8,
                border: 'none',
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: 14,
                fontFamily: 'Nunito',
                background: tab === item.id ? 'var(--cream3)' : 'transparent',
                color: tab === item.id ? 'var(--terra)' : 'var(--ink-mid)',
                borderLeft: tab === item.id ? '3px solid var(--terra)' : '3px solid transparent',
                boxShadow: tab === item.id ? 'var(--shadow-sm)' : 'none',
                transition: 'all 0.15s',
              }}
            >
              <span style={{ fontSize: 18 }}>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* logout */}
        <div style={{ padding: '14px 10px', borderTop: 'var(--border)' }}>
          <button
            onClick={onLogout}
            className="btn"
            style={{
              width: '100%',
              fontSize: 13,
              background: 'transparent',
              color: 'var(--ink-mid)',
              borderColor: 'var(--gold)',
            }}
          >
            Sign out
          </button>
        </div>
      </div>

      {/* ─── MAIN CONTENT ─── */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        background: 'var(--cream)',
        display: 'flex',
        flexDirection: 'column',
      }}>  {/* Appshell receives token from App.jsx then hands down to LogScreen so it can call the API */}
        {tab === 'log'      && <LogScreen token={token} />}   
        {tab === 'history'  && <HistoryScreen token={token} />}
        {tab === 'chat' && <ChatScreen token={token} />}
        {tab === 'insights' && <InsightsScreen token={token} />}
      </div>
    </div>
  );
}

/* placeholder for tabs we haven't built yet */
function ComingSoon({ name, icon }) {
  return (
    <div style={{
      padding: 60,
      textAlign: 'center',
      maxWidth: 500,
      margin: '60px auto 0',
    }}>
      <div style={{ fontSize: 64, marginBottom: 16 }}>{icon}</div>
      <h2 style={{
        fontFamily: 'Lora',
        fontStyle: 'italic',
        fontSize: 28,
        color: 'var(--ink)',
        marginBottom: 8,
      }}>
        {name}
      </h2>
      <p style={{ color: 'var(--ink-lt)', fontWeight: 600, fontSize: 14 }}>
        Coming in the next session — we're shipping one screen at a time. ✨
      </p>
    </div>
  );
}

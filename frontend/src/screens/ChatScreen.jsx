/**
 *  ChatScreen
 * 
 * Conversation interface with the MAKANAI nutrition assistant.
 * Loads past chat history on mount, sends new messages to the 
 * non-streaming chat endpoint, displays user + assistant bubbles 
 * with optimistic UI for instant feedback 
 * 
 * Data flow:
 *      on mount       -> GET /api/chat/history (load past messages)
 *      on send        -> optimistic user bubble + typing indicator
 *                        POST /api/chat with {messages}
 *                        replace typing indicator with assistant reply
 * 
 * Props:
 *      token (string)  - JWT access token, passed from AppShell 
 * 
 * Used by: 
 *      AppShell.jsx (when tab === "chat")
 * 
 * Notes:
 *      - First reply can take 20-30s as Ollama warms up phi3
 *      - Uses non-streaming endpoint for simplicity. Backend has a 
 *        /stream variant which wills swap later
 */

import { useState, useEffect, useRef } from "react";
import { api } from '../api/client'
import Spinner from '../components/Spinner'

export default function ChatScreen({ token }) {
    const [messages, setMessages] = useState([]);   // [{role, message, id}]
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [historyLoading, setHistoryLoading] = useState(true);
    const [error, setError] = useState('');

    const scrollRef = useRef(null); // ref to scroll the container 
    const inputRef = useRef(null);  // ref to the textarea

    // --------- Load chat history on mount ----------
    useEffect(() => {
  console.log('🟢 useEffect running, token:', token ? 'present' : 'MISSING');
  let cancelled = false;
  const load = async () => {
    console.log('1. starting history fetch');
    try {
      const data = await api.get('/api/chat/history', token);
      console.log('2. got data:', data);
      console.log('   data is array?', Array.isArray(data));
      console.log('   data length:', data?.length);
      if (!cancelled) {
        console.log('3. calling setMessages with', data);
        setMessages(data || []);
        console.log('4. setMessages called');
      } else {
        console.log('   CANCELLED - not setting messages');
      }
    } catch (err) {
      console.log('5. CAUGHT ERROR:', err);
      if (!cancelled) setError(err.message);
    } finally {
      console.log('6. finally block, cancelled?', cancelled);
      if (!cancelled) {
        setHistoryLoading(false);
        console.log('7. setHistoryLoading(false) called');
      }
    }
  };
  load();
  return () => { 
    console.log('🔴 cleanup running, cancelling');
    cancelled = true; 
  };
    }, [token]);

    // ----------- Auto scroll to bottom when message change -----
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, sending]);

    // ----------- Send Message -------------------
    const send = async () => {
        const text = input.trim();
        if (!text || sending) return; 

        setError('');
        setInput('');
        setSending(true);

        // optimistic user bubble - appears instantly 
        const tempId = 'temp-' + Date.now();
        setMessages(prev => [
            ...prev, 
            {id: tempId, role: 'user', message: text, created_at: new Date().toISOString()}
        ]); 

        try {
            const data = await api.post('/api/chat', { message: text }, token); 
            setMessages(prev => [
                ...prev,
                {
                    id: 'assistant-' + Date.now(),
                    role: 'assistant', 
                    message: data.reply, 
                    created_at: new Date().toISOString(),
                },
            ]);
        } catch (err){ 
            setError(err.message);
            // remove the optimistic bubble on error so user can retry 
            setMessages(prev => prev.filter(m => m.id !== tempId));
            setInput(text); // restore their input
        } finally { 
            setSending(false);
            inputRef.current?.focus()
        }
    };

    const onKeyDown = (e) => {
        // Enter sends, Shift+Enter newlines
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); 
            send();
        }
    };

    // ─── render ─────────────────────────────────────
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* heading */}
      <div style={{ padding: '24px 40px 16px', borderBottom: 'var(--border)', flexShrink: 0 }}>
        <h1 style={{ fontFamily: 'Lora', fontStyle: 'italic', fontWeight: 700, fontSize: 26, color: 'var(--ink)' }}>
          AI Chat 💬
        </h1>
        <p style={{ fontSize: 13, color: 'var(--ink-lt)', fontWeight: 600, marginTop: 2 }}>
          Ask me anything about your meals or nutrition.
        </p>
      </div>

      {/* messages */}
      <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', padding: '20px 40px' }}>
        {historyLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 60 }}>
            <Spinner size={32} />
          </div>
        ) : messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 720, margin: '0 auto' }}>
            {messages.map(msg => (
              <Bubble key={msg.id} role={msg.role} text={msg.message} />
            ))}
            {sending && <TypingBubble />}
          </div>
        )}
      </div>

      {/* error */}
      {error && (
        <div style={{ padding: '8px 40px', flexShrink: 0 }}>
          <div style={{ background: '#FDE8E0', border: '1px solid var(--terra)', borderRadius: 8, padding: '8px 12px', fontSize: 12, color: 'var(--terra)', fontWeight: 600 }}>
            ⚠ {error}
          </div>
        </div>
      )}

      {/* input bar */}
      <div style={{ padding: '14px 40px 18px', borderTop: 'var(--border)', flexShrink: 0, background: 'var(--cream)' }}>
        <div style={{ display: 'flex', gap: 10, maxWidth: 720, margin: '0 auto', alignItems: 'flex-end' }}>
          <textarea
            ref={inputRef}
            className="input-field"
            rows={1}
            placeholder="Ask about your meals, nutrition, or healthy eating..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={sending}
            style={{ resize: 'none', flex: 1, fontSize: 14, lineHeight: 1.4, padding: '10px 14px', minHeight: 42, maxHeight: 120 }}
          />
          <button
            className="btn btn-primary"
            onClick={send}
            disabled={sending || !input.trim()}
            style={{ padding: '0 18px', height: 42, fontSize: 14, flexShrink: 0 }}
          >
            {sending ? <Spinner size={16} color="white" /> : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Bubble ───────────────────────────────── */
function Bubble({ role, text }) {
  const isUser = role === 'user';
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
    }}>
      <div className="fadeUp" style={{
        maxWidth: '78%',
        padding: '10px 14px',
        borderRadius: 14,
        background: isUser ? 'var(--terra)' : 'var(--cream3)',
        color: isUser ? '#FBF5E8' : 'var(--ink)',
        border: isUser ? 'none' : 'var(--border)',
        fontSize: 14,
        fontWeight: 500,
        lineHeight: 1.5,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        boxShadow: 'var(--shadow-sm)',
      }}>
        {text}
      </div>
    </div>
  );
}

/* ─── TypingBubble (the "..." indicator) ───── */
function TypingBubble() {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
      <div className="fadeUp" style={{
        padding: '12px 16px',
        borderRadius: 14,
        background: 'var(--cream3)',
        border: 'var(--border)',
        boxShadow: 'var(--shadow-sm)',
        display: 'flex',
        gap: 4,
      }}>
        <Dot delay="0s" />
        <Dot delay="0.2s" />
        <Dot delay="0.4s" />
      </div>
    </div>
  );
}

function Dot({ delay }) {
  return (
    <span style={{
      width: 6, height: 6, borderRadius: '50%',
      background: 'var(--ink-lt)',
      animation: 'pulse 1.2s infinite ease-in-out',
      animationDelay: delay,
    }} />
  );
}

/* ─── EmptyState ───────────────────────────── */
function EmptyState() {
  return (
    <div style={{ textAlign: 'center', maxWidth: 460, margin: '60px auto 0' }}>
      <div style={{ fontSize: 56, marginBottom: 14 }}>💬</div>
      <h2 style={{ fontFamily: 'Lora', fontStyle: 'italic', fontSize: 24, color: 'var(--ink)', marginBottom: 8 }}>
        Selamat datang!
      </h2>
      <p style={{ color: 'var(--ink-lt)', fontWeight: 600, fontSize: 14, lineHeight: 1.5 }}>
        I know your last 10 meals — ask me anything about your protein intake,
        calorie balance, or healthy Malaysian food swaps.
      </p>
    </div>
  );
}
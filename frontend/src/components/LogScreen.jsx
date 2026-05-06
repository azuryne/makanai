// log meal page 

import { useState } from 'react';
import { api } from '../api/client';
import Spinner from '../components/Spinner';
import MacroRing from '../components/MacroRing';
import NutriBadge from '../components/NutriBadge';

const EXAMPLES = [
  'nasi lemak with extra sambal and teh tarik',
  'roti canai with dhal curry for breakfast',
  'char kway teow and sugarcane juice for lunch',
  'mee goreng mamak and teh ais for dinner',
];

const MEAL_TIMES = ['breakfast', 'lunch', 'dinner', 'snack'];

export default function LogScreen({ token }) {
  const [text, setText] = useState('');
  const [mealTime, setMealTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const submit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await api.post(
        '/api/meals/log',
        { text: text.trim(), meal_time: mealTime || undefined },
        token
      );
      setResult(data);
      setText('');
      setMealTime('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '32px 40px', maxWidth: 760, margin: '0 auto', width: '100%' }}>
      {/* heading */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{
          fontFamily: 'Lora',
          fontStyle: 'italic',
          fontWeight: 700,
          fontSize: 32,
          color: 'var(--ink)',
        }}>
          Log a Meal 🍛
        </h1>
        <p style={{ fontSize: 14, color: 'var(--ink-lt)', fontWeight: 600, marginTop: 4 }}>
          Tell me what you ate — I'll figure out the rest.
        </p>
      </div>

      {/* input card */}
      <div className="card" style={{ padding: 24, marginBottom: 20 }}>
        <label style={{ display: 'block', fontSize: 12, fontWeight: 800, color: 'var(--ink-mid)', marginBottom: 6 }}>
          What did you eat?
        </label>
        <textarea
          className="input-field"
          rows={3}
          placeholder="nasi lemak with teh tarik..."
          value={text}
          onChange={e => setText(e.target.value)}
          style={{ marginBottom: 14, resize: 'none' }}
        />

        <label style={{ display: 'block', fontSize: 12, fontWeight: 800, color: 'var(--ink-mid)', marginBottom: 6 }}>
          Meal time (optional)
        </label>
        <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap' }}>
          {MEAL_TIMES.map(mt => (
            <button
              key={mt}
              type="button"
              onClick={() => setMealTime(mealTime === mt ? '' : mt)}
              style={{
                padding: '8px 14px',
                border: 'var(--border)',
                borderRadius: 8,
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: 13,
                fontFamily: 'Nunito',
                background: mealTime === mt ? 'var(--gold)' : 'var(--cream3)',
                color: mealTime === mt ? '#FBF5E8' : 'var(--ink-mid)',
                textTransform: 'capitalize',
                boxShadow: 'var(--shadow-sm)',
                transition: 'all 0.15s',
              }}
            >
              {mt}
            </button>
          ))}
        </div>

        <button
          className="btn btn-primary"
          onClick={submit}
          disabled={loading || !text.trim()}
          style={{ width: '100%', padding: 12, fontSize: 15 }}
        >
          {loading && <Spinner size={18} color="white" />}
          {loading ? 'Analyzing...' : 'Log Meal ✨'}
        </button>
      </div>

      {/* example chips */}
      {!result && !loading && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--ink-lt)', marginBottom: 8 }}>
            Try an example:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => setText(ex)}
                style={{
                  padding: '6px 12px',
                  border: '1px dashed #C0A060',
                  borderRadius: 16,
                  background: 'transparent',
                  fontSize: 12,
                  color: 'var(--ink-mid)',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontFamily: 'Nunito',
                }}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* error */}
      {error && (
        <div style={{
          background: '#FDE8E0',
          border: '1px solid var(--terra)',
          borderRadius: 8,
          padding: '12px 16px',
          fontSize: 13,
          color: 'var(--terra)',
          fontWeight: 600,
          marginBottom: 20,
        }}>
          ⚠ {error}
        </div>
      )}

      {/* result card */}
      {result && (
        <div className="card fadeUp" style={{ padding: 28 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 20,
            flexWrap: 'wrap',
            gap: 16,
          }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--ink-lt)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Logged
              </div>
              <div style={{ fontFamily: 'Lora', fontStyle: 'italic', fontSize: 22, fontWeight: 700, color: 'var(--ink)', marginTop: 2 }}>
                {result.raw_text}
              </div>
              {result.meal_time && (
                <div style={{ fontSize: 12, color: 'var(--ink-mid)', fontWeight: 700, marginTop: 4, textTransform: 'capitalize' }}>
                  🕐 {result.meal_time}
                </div>
              )}
            </div>
            <MacroRing calories={result.nutrition?.calories || 0} />
          </div>

          {/* parsed foods */}
          {result.parsed_food?.length > 0 && (
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--ink-lt)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
                Detected foods
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {result.parsed_food.map((food, i) => (
                  <span key={i} style={{
                    background: 'var(--cream2)',
                    border: 'var(--border)',
                    borderRadius: 16,
                    padding: '4px 12px',
                    fontSize: 12,
                    fontWeight: 700,
                    color: 'var(--ink)',
                  }}>
                    {food}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* macro badges */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <NutriBadge label="Protein" value={result.nutrition?.protein || 0} unit="g" color="#F2E0C8" />
            <NutriBadge label="Carbs"   value={result.nutrition?.carbs   || 0} unit="g" color="#D4E8D0" />
            <NutriBadge label="Fat"     value={result.nutrition?.fat     || 0} unit="g" color="#E8D8F0" />
            <NutriBadge label="Fiber"   value={result.nutrition?.fiber   || 0} unit="g" color="#FBE8C8" />
          </div>

          {/* source */}
          {result.nutrition?.source && (
            <div style={{ marginTop: 16, fontSize: 11, color: 'var(--ink-lt)', fontWeight: 600, fontStyle: 'italic' }}>
              Source: {result.nutrition.source}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
/**
 *  HistoryScreen 
 * 
 *  Displays a chronologicasl list of all meals the user has logged.
 *  Shows meal text, parsed foods, nutrition, meal time, and timestamp
 * 
 * Data Flow:
 *  on mount -> GET /api/meals/history (with JWT)
 *           -> list of meal records, newest first
 *           -> rendered as a scroll of MealCards
 * 
 * Props:
 *  token (string) - JWT access token, passed from AppShell
 * 
 * Used by: AppShell.jsx (when tab == 'history')
 */

import { useState, useEffect } from "react";
import { api } from '../api/client';
import Spinner from '../components/Spinner';
import NutriBadge from '../components/NutriBadge';

export default function HistoryScreen({ token }) {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await api.get('/api/meals/history', token);
        if (!cancelled) setMeals(data.meals || []);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [token]);

  // ─── loading ───
  if (loading) {
    return (
      <div style={{ padding: 60, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <Spinner size={40} />
        <div style={{ fontFamily: 'Lora', fontStyle: 'italic', color: 'var(--ink-lt)', fontSize: 14 }}>
          Loading your meals...
        </div>
      </div>
    );
  }

  // ─── error ───
  if (error) {
    return (
      <div style={{ padding: 40, maxWidth: 600, margin: '0 auto' }}>
        <div style={{ background: '#FDE8E0', border: '1px solid var(--terra)', borderRadius: 8, padding: '12px 16px', fontSize: 13, color: 'var(--terra)', fontWeight: 600 }}>
          ⚠ {error}
        </div>
      </div>
    );
  }

  // ─── empty ───
  if (meals.length === 0) {
    return (
      <div style={{ padding: 60, textAlign: 'center', maxWidth: 500, margin: '60px auto 0' }}>
        <div style={{ fontSize: 64, marginBottom: 16 }}>📖</div>
        <h2 style={{ fontFamily: 'Lora', fontStyle: 'italic', fontSize: 28, color: 'var(--ink)', marginBottom: 8 }}>
          No meals yet
        </h2>
        <p style={{ color: 'var(--ink-lt)', fontWeight: 600, fontSize: 14 }}>
          Head to <strong>Log Meal</strong> and tell me what you ate today. ✨
        </p>
      </div>
    );
  }

  // ─── data ───
  return (
    <div style={{ padding: '32px 40px', maxWidth: 760, margin: '0 auto', width: '100%' }}>
      {/* heading */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontFamily: 'Lora', fontStyle: 'italic', fontWeight: 700, fontSize: 32, color: 'var(--ink)' }}>
          Meal History 📖
        </h1>
        <p style={{ fontSize: 14, color: 'var(--ink-lt)', fontWeight: 600, marginTop: 4 }}>
          {meals.length} meal{meals.length === 1 ? '' : 's'} logged
        </p>
      </div>

      {/* list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {meals.map((meal, i) => (
          <MealCard key={meal.meal_id || i} meal={meal} />
        ))}
      </div>
    </div>
  );
}

/* ───────────────────────────────────────────────
   MealCard - one row in the history list
─────────────────────────────────────────────── */
function MealCard({ meal }) {
  const cal = meal.nutrition?.calories || 0;
  const foods = meal.parsed_foods || [];
  const source = meal.nutrition?.source;

  return (
    <div className="card fadeUp" style={{ padding: 20 }}>
      {/* top row: text + calories */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, marginBottom: 10, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 200 }}>
          <div style={{ fontFamily: 'Lora', fontStyle: 'italic', fontSize: 17, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.3 }}>
            {meal.raw_text}
          </div>
          <div style={{ fontSize: 11, color: 'var(--ink-mid)', fontWeight: 700, marginTop: 4, textTransform: 'capitalize' }}>
            {meal.meal_time && <>🕐 {meal.meal_time} · </>}
            {formatTimeAgo(meal.logged_at)}
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontFamily: 'Baloo 2', fontSize: 22, fontWeight: 800, color: 'var(--terra)', lineHeight: 1 }}>
            {Math.round(cal)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--ink-lt)', fontWeight: 700, marginTop: 2 }}>
            kcal
          </div>
        </div>
      </div>

      {/* food chips */}
      {foods.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 12 }}>
          {foods.map((f, i) => (
            <span key={i} style={{ background: 'var(--cream2)', border: 'var(--border)', borderRadius: 14, padding: '3px 10px', fontSize: 11, fontWeight: 700, color: 'var(--ink)' }}>
              {f}
            </span>
          ))}
        </div>
      )}

      {/* macros */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <NutriBadge label="Protein" value={meal.nutrition?.protein || 0} unit="g" color="#F2E0C8" />
        <NutriBadge label="Carbs"   value={meal.nutrition?.carbs   || 0} unit="g" color="#D4E8D0" />
        <NutriBadge label="Fat"     value={meal.nutrition?.fat     || 0} unit="g" color="#E8D8F0" />
        <NutriBadge label="Fiber"   value={meal.nutrition?.fiber   || 0} unit="g" color="#FBE8C8" />
      </div>

      {/* source badge */}
      {source && (
        <div style={{ marginTop: 12, fontSize: 10, color: 'var(--ink-lt)', fontWeight: 600, fontStyle: 'italic' }}>
          Source: {source}
        </div>
      )}
    </div>
  );
}

/* ───────────────────────────────────────────────
   formatTimeAgo - "2h ago", "3d ago", etc.
─────────────────────────────────────────────── */
function formatTimeAgo(iso) {
  if (!iso) return '';
  const then = new Date(iso);
  const now = new Date();
  const diffMs = now - then;
  const mins = Math.floor(diffMs / 60000);
  const hours = Math.floor(mins / 60);
  const days = Math.floor(hours / 24);

  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return then.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
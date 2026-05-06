// Little pill-shaped boxes that show one nutrient each 

export default function NutriBadge({ label, value, unit = 'g', color = 'var(--cream3)' }) {
  return (
    <div style={{
      textAlign: 'center',
      background: color,
      border: '1px solid #C0A060',
      borderRadius: 10,
      padding: '8px 12px',
      minWidth: 72,
    }}>
      <div style={{
        fontSize: 16,
        fontWeight: 800,
        fontFamily: 'Baloo 2',
        color: 'var(--ink)',
      }}>
        {Math.round(value)}
        <span style={{ fontSize: 10, fontWeight: 700 }}>{unit}</span>
      </div>
      <div style={{
        fontSize: 11,
        color: 'var(--ink-mid)',
        fontWeight: 700,
      }}>
        {label}
      </div>
    </div>
  );
}
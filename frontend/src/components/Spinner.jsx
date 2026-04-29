// Will be reused for every loading state

export default function Spinner({ size = 20, color = 'var(--gold)' }) {   // export default → other files can do import Spinner from './Spinner'.
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      style={{ animation: 'spin 0.8s linear infinite', flexShrink: 0 }}
    >
      <circle
        cx="12" cy="12" r="9"
        fill="none" stroke={color} strokeWidth="2.5"
        strokeDasharray="40 20" strokeLinecap="round"
      />
    </svg>
  );
}
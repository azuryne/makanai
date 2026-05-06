// Circular calorie meter. Takes calories number and a goal number, 

export default function MacroRing( { calories = 0, goal = 1950, size = 110}) {
    const pct = Math.min(calories / goal, 1);
    const r = 42;
    const circ = 2 * Math.PI * r;

    return (
        <div style={{ position: 'relative', width: size, height: size}}>
            <svg
                width={size}
                height={size}
                viewbox="0 0 96 96"
                style={{ transform: 'rotate(-90deg' }}
            >
                {/* background ring (cream) */}
                <circle cx="48" cy="48" r={r} fill="none" stroke="#EDE1C5" strokeWidth="8" />

                {/* foreground ring (terra) - fills based on pct */}
                <circle 
                    cx="48" cy="48" r={r}
                    fill="none"
                    stroke="var(--terra)"
                    strokeWidth="8"
                    strokeDasharray={`${circ * pct} ${circ}`}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dasharray 0.6s ease' }}
                    />
                </svg>

                {/* number in the middle */}
                <div style={{
                    position: 'absolute', inset: 0,
                    display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center',
                }}>
                    <div style={{
                    fontFamily: 'Baloo 2',
                    fontSize: size * 0.2,
                    fontWeight: 800,
                    lineHeight: 1,
                    color: 'var(--ink)',
                    }}>
                    {Math.round(calories)}
                    </div>
                    <div style={{
                    fontSize: size * 0.1,
                    fontWeight: 700,
                    color: 'var(--ink-lt)',
                    }}>
                    / {goal} kcal
                    </div>
                </div>
            </div>
            );
            }
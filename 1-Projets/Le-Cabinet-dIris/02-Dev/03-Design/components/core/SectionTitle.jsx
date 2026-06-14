import React from 'react';

/**
 * Titre de section centré avec filets dorés latéraux (« Sélection d'Iris »).
 */
export function SectionTitle({ children, subtitle, onDark = false }) {
  const lineStyle = { flex: 1, height: 1, background: 'var(--color-border)', maxWidth: 120 };
  return (
    <div style={{ textAlign: 'center', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20 }}>
        <div style={lineStyle}></div>
        <h2
          style={{
            fontFamily: 'var(--font-serif-display)',
            fontWeight: 600,
            fontSize: '1.6rem',
            letterSpacing: '0.06em',
            color: onDark ? 'var(--color-text-on-dark)' : 'var(--color-primary)',
            margin: 0,
            whiteSpace: 'nowrap',
          }}
        >
          {children}
        </h2>
        <div style={lineStyle}></div>
      </div>
      {subtitle ? (
        <p
          style={{
            fontFamily: 'var(--font-sans-body)',
            fontWeight: 300,
            fontSize: 13,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: 'var(--color-accent)',
            margin: '10px 0 0',
          }}
        >
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}

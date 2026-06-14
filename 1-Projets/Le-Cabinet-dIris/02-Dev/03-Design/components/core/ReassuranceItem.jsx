import React from 'react';

/**
 * Bloc de réassurance — icône trait or + libellé ivoire, sur fond noir d'encre.
 * Icône : passer un nœud React (ex. SVG Lucide inline) via `icon`.
 */
export function ReassuranceItem({ icon, label }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 10,
        textAlign: 'center',
        padding: 10,
        color: 'var(--color-accent)',
      }}
    >
      <span style={{ width: 26, height: 26, display: 'block' }}>{icon}</span>
      <span
        style={{
          fontFamily: 'var(--font-sans-body)',
          fontWeight: 300,
          fontSize: 12,
          letterSpacing: '0.08em',
          color: 'var(--color-text-on-dark)',
        }}
      >
        {label}
      </span>
    </div>
  );
}

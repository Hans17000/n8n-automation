import React from 'react';

/**
 * Séparateur — filet doré avec motif central (monogramme « I » ou fleuron).
 */
export function Separator({ motif = 'I', onDark = false, style }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, ...style }}>
      <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }}></div>
      <span
        style={{
          fontFamily: 'var(--font-serif-display)',
          fontSize: 16,
          lineHeight: 1,
          color: 'var(--color-accent)',
        }}
      >
        {motif}
      </span>
      <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }}></div>
    </div>
  );
}

import React from 'react';

/**
 * Citation d'Iris — Pinyon Script sur fond sombre, guillemets dorés.
 */
export function IrisQuote({ children, attribution = 'Iris' }) {
  return (
    <div style={{ textAlign: 'center', padding: '30px 20px' }}>
      <span
        style={{
          fontFamily: 'var(--font-serif-display)',
          fontSize: 32,
          color: 'var(--color-accent)',
          lineHeight: 1,
          display: 'block',
          marginBottom: 4,
        }}
      >
        «
      </span>
      <p
        style={{
          fontFamily: 'var(--font-script)',
          fontSize: 'var(--text-quote, 20px)',
          color: 'var(--color-text-on-dark)',
          margin: 0,
          maxWidth: 500,
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      >
        {children}
      </p>
      <span
        style={{
          fontFamily: 'var(--font-sans-body)',
          fontWeight: 300,
          fontSize: 11,
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: 'var(--color-accent)',
          display: 'block',
          marginTop: 10,
        }}
      >
        {attribution}
      </span>
    </div>
  );
}

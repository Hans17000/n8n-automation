import React from 'react';

/**
 * Badge produit : « Pièce rare » (bordeaux, bord doré) ou « Cabinet » (prune).
 */
export function Badge({ variant = 'rare', children }) {
  const styles = {
    rare: { backgroundColor: 'var(--color-alert)', border: '0.5px solid var(--color-border-strong)' },
    cabinet: { backgroundColor: 'var(--color-cabinet)', border: 'none' },
  };
  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: 'var(--font-sans-body)',
        fontSize: 11,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        padding: '4px 12px',
        borderRadius: 1,
        color: 'var(--color-text-on-dark)',
        ...styles[variant],
      }}
    >
      {children || (variant === 'rare' ? 'Pièce rare' : 'Cabinet')}
    </span>
  );
}

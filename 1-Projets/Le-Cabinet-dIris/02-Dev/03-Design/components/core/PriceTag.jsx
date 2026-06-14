import React from 'react';

/**
 * Prix — Lato Light 300 doré, letter-spacing 0.05em.
 */
export function PriceTag({ amount, size = 'md', currency = '€' }) {
  const sizes = { sm: 14, md: 16, lg: '1.6rem' };
  const formatted = typeof amount === 'number'
    ? amount.toFixed(2).replace('.', ',')
    : amount;
  return (
    <span
      style={{
        fontFamily: 'var(--font-sans-body)',
        fontWeight: 300,
        fontSize: sizes[size],
        color: 'var(--color-accent)',
        letterSpacing: '0.05em',
      }}
    >
      {formatted}&nbsp;{currency}
    </span>
  );
}

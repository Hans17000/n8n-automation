import React from 'react';
import { PriceTag } from '../core/PriceTag.jsx';
import { Badge } from '../core/Badge.jsx';

/**
 * Miniature produit — fond ivoire, hairline dorée, bordure or plein au hover.
 */
export function ProductCard({ name, price, image, badge, category, onClick }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: 'var(--color-background)',
        border: `0.5px solid ${hover ? 'var(--color-accent)' : 'var(--color-border)'}`,
        transition: 'border-color 0.3s ease',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
      }}
    >
      {badge ? (
        <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 1 }}>
          <Badge variant={badge} />
        </div>
      ) : null}
      <div
        style={{
          aspectRatio: '3 / 4',
          background: 'var(--color-background-dark)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {image ? (
          <img src={image} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <span
            style={{
              fontFamily: 'var(--font-serif-display)',
              fontSize: 28,
              color: 'var(--color-border)',
              border: '1px solid var(--color-border)',
              borderRadius: '50%',
              width: 48,
              height: 62,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            I
          </span>
        )}
      </div>
      <div style={{ padding: '14px 16px 18px', textAlign: 'center' }}>
        {category ? (
          <span
            style={{
              fontFamily: 'var(--font-sans-body)',
              fontWeight: 300,
              fontSize: 10.5,
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: 'var(--color-text-secondary)',
              display: 'block',
              marginBottom: 4,
            }}
          >
            {category}
          </span>
        ) : null}
        <h3
          style={{
            fontFamily: 'var(--font-serif-display)',
            fontWeight: 600,
            fontSize: 17,
            letterSpacing: '0.02em',
            color: 'var(--color-primary)',
            margin: '0 0 6px',
          }}
        >
          {name}
        </h3>
        <PriceTag amount={price} />
      </div>
    </div>
  );
}

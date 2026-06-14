import React from 'react';

/**
 * Tuile d'univers / catégorie — fond sombre (encre ou prune), nom serif, sous-texte.
 */
export function CategoryTile({ name, description, tone = 'vitrine', onClick, height = 220 }) {
  const [hover, setHover] = React.useState(false);
  const bg = tone === 'cabinet' ? 'var(--color-cabinet)' : 'var(--color-primary)';
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: bg,
        border: `1px solid ${hover ? 'var(--color-accent)' : 'var(--color-border)'}`,
        transition: 'border-color 0.3s ease',
        cursor: onClick ? 'pointer' : 'default',
        height,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
        textAlign: 'center',
        padding: '20px 24px',
        boxSizing: 'border-box',
      }}
    >
      <h3
        style={{
          fontFamily: 'var(--font-serif-display)',
          fontWeight: 400,
          fontSize: 24,
          letterSpacing: '0.08em',
          color: 'var(--color-text-on-dark)',
          margin: 0,
        }}
      >
        {name}
      </h3>
      {description ? (
        <p
          style={{
            fontFamily: 'var(--font-sans-body)',
            fontWeight: 300,
            fontStyle: 'italic',
            fontSize: 13,
            color: 'var(--color-accent-light)',
            margin: 0,
            maxWidth: 260,
            lineHeight: 1.6,
          }}
        >
          {description}
        </p>
      ) : null}
      <span
        style={{
          fontFamily: 'var(--font-serif-display)',
          fontSize: 12,
          textTransform: 'uppercase',
          letterSpacing: '0.15em',
          color: 'var(--color-accent)',
          borderBottom: `1px solid ${hover ? 'var(--color-accent)' : 'transparent'}`,
          transition: 'border-color 0.3s ease',
          marginTop: 6,
        }}
      >
        Découvrir
      </span>
    </div>
  );
}

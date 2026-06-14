import React from 'react';

/**
 * Bouton Le Cabinet d'Iris.
 * variant: 'primary' (fond or) | 'secondary' (outline or) | 'cabinet-entry' (italique, « Poussez la porte ») | 'ghost' (lien souligné discret)
 */
export function Button({ variant = 'primary', children, href, onClick, disabled = false, style }) {
  const [hover, setHover] = React.useState(false);

  const base = {
    display: 'inline-block',
    fontFamily: 'var(--font-serif-display)',
    fontSize: 'var(--text-btn, 14px)',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    textDecoration: 'none',
    cursor: disabled ? 'default' : 'pointer',
    transition: 'all 0.3s ease',
    borderRadius: 0,
    boxSizing: 'border-box',
    opacity: disabled ? 0.4 : 1,
    pointerEvents: disabled ? 'none' : 'auto',
  };

  const variants = {
    primary: {
      backgroundColor: hover ? 'var(--color-btn-primary-hover)' : 'var(--color-btn-primary-bg)',
      color: 'var(--color-btn-primary-text)',
      border: 'none',
      padding: '14px 40px',
    },
    secondary: {
      backgroundColor: hover ? 'var(--color-accent)' : 'transparent',
      color: hover ? 'var(--color-primary)' : 'var(--color-btn-secondary-text)',
      border: '1px solid var(--color-btn-secondary-border)',
      padding: '12px 40px',
      letterSpacing: '0.15em',
    },
    'cabinet-entry': {
      backgroundColor: hover ? 'var(--color-accent)' : 'transparent',
      color: hover ? 'var(--color-primary)' : 'var(--color-accent)',
      border: '1px solid var(--color-accent)',
      padding: '6px 18px',
      borderRadius: 2,
      fontStyle: 'italic',
      textTransform: 'none',
      letterSpacing: '0.05em',
      fontSize: 15,
    },
    ghost: {
      backgroundColor: 'transparent',
      color: 'var(--color-text-on-dark)',
      border: 'none',
      padding: 0,
      fontFamily: 'var(--font-sans-body)',
      fontSize: 13,
      textTransform: 'none',
      letterSpacing: '0.02em',
      textDecoration: 'underline',
      opacity: disabled ? 0.4 : hover ? 0.9 : 0.5,
    },
  };

  const Tag = href ? 'a' : 'button';
  return (
    <Tag
      href={href}
      onClick={onClick}
      disabled={disabled}
      style={{ ...base, ...variants[variant], ...style }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {children}
    </Tag>
  );
}

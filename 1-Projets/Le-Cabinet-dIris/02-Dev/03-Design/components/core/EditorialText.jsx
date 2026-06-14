import React from 'react';

/**
 * Texte éditorial de catégorie — italique centré entre deux filets dorés, max 700px.
 */
export function EditorialText({ children }) {
  return (
    <div
      style={{
        maxWidth: 'var(--measure-editorial, 700px)',
        margin: '0 auto',
        textAlign: 'center',
        fontFamily: 'var(--font-sans-body)',
        fontStyle: 'italic',
        fontSize: 15,
        color: 'var(--color-text-secondary)',
        lineHeight: 1.8,
        padding: '30px 20px',
        borderTop: '1px solid var(--color-border)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      {children}
    </div>
  );
}

// Écrans — Le Cabinet d'Iris
const DS_screens = window.LeCabinetDIrisDesignSystem_55ae4c;

// ── Homepage ──────────────────────────────────────────────
function HomePage({ go }) {
  const { Button, SectionTitle, IrisQuote, ProductCard, CategoryTile, Separator } = DS_screens;
  return (
    <div>
      {/* Hero — photo clair-obscur à fournir (aplat noir d'encre en attendant) */}
      <section style={{
        position: 'relative', height: 440, background: 'var(--color-primary-dark)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center',
      }}>
        <div style={{ padding: 40 }}>
          <h1 style={{
            fontFamily: 'var(--font-serif-display)', fontSize: '3.5rem', fontWeight: 400,
            color: 'var(--color-text-on-dark)', letterSpacing: '0.1em', margin: '0 0 10px',
          }}>Le Cabinet d'Iris</h1>
          <p style={{
            fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: '1.1rem',
            color: 'var(--color-accent)', letterSpacing: '0.2em', textTransform: 'uppercase',
            margin: '0 0 40px',
          }}>Collection privée de curiosités sensuelles</p>
          <Button variant="secondary" onClick={() => go('category', { category: 'Les Étoffes' })}>Entrer dans la Vitrine</Button>
        </div>
        <span style={{
          position: 'absolute', bottom: 14, right: 18, fontFamily: 'var(--font-sans-body)',
          fontWeight: 300, fontSize: 10, letterSpacing: '0.1em', color: 'var(--color-text-on-dark)', opacity: 0.35,
        }}>Photo clair-obscur à fournir</span>
      </section>

      {/* Sélection d'Iris */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '60px 40px 50px' }}>
        <SectionTitle subtitle="Quatre pièces choisies">Sélection d'Iris</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginTop: 36 }}>
          {HOME_SELECTION.map((p) => (
            <ProductCard key={p.name} {...p} onClick={() => go('product', { product: p, category: p.category })} />
          ))}
        </div>
      </section>

      {/* Les univers */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '10px 40px 60px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
          <CategoryTile name="La Vitrine" height={260}
            description="Lingerie fine, nuits de soie et élixirs d'alcôve — l'étage que l'on visite en plein jour."
            onClick={() => go('category', { category: 'Les Étoffes' })} />
          <CategoryTile name="Le Cabinet" tone="cabinet" height={260}
            description="Iris a rassemblé ici ce qu'elle ne montre qu'à ceux qui poussent la porte."
            onClick={() => go('gate')} />
        </div>
      </section>

      {/* Citation */}
      <section style={{ background: 'var(--color-primary)', padding: '26px 0' }}>
        <IrisQuote>Le désir est une curiosité qui se collectionne.</IrisQuote>
      </section>

      {/* Les Carnets d'Iris */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '56px 40px 70px' }}>
        <SectionTitle subtitle="Le journal de la maison">Les Carnets d'Iris</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18, marginTop: 36 }}>
          {CARNETS.map((c) => (
            <CarnetCard key={c.title} {...c} />
          ))}
        </div>
      </section>
    </div>
  );
}

function CarnetCard({ title, date }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        border: `0.5px solid ${hover ? 'var(--color-accent)' : 'var(--color-border)'}`,
        transition: 'border-color 0.3s ease', padding: '26px 24px 24px', cursor: 'pointer',
        background: 'var(--color-background)',
      }}>
      <span style={{ color: 'var(--color-accent)', display: 'block', marginBottom: 12 }}><IconFeather size={22} /></span>
      <h3 style={{
        fontFamily: 'var(--font-serif-display)', fontWeight: 600, fontSize: 19,
        color: 'var(--color-primary)', margin: '0 0 8px', letterSpacing: '0.02em',
      }}>{title}</h3>
      <span style={{
        fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 11.5,
        letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--color-text-secondary)',
      }}>{date}</span>
    </div>
  );
}

// ── Sas du Cabinet ────────────────────────────────────────
function GatePage({ go }) {
  const { Button } = DS_screens;
  return (
    <section style={{
      minHeight: 560, background: 'var(--color-primary)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', textAlign: 'center',
    }}>
      <div style={{ padding: 40 }}>
        <div style={{
          width: 64, height: 82, margin: '0 auto 28px', border: '1px solid var(--color-accent)',
          borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-serif-display)', fontSize: 38, color: 'var(--color-accent)', opacity: 0.85,
        }}>I</div>
        <h1 style={{
          fontFamily: 'var(--font-serif-display)', fontSize: '2.5rem', fontWeight: 400,
          color: 'var(--color-text-on-dark)', letterSpacing: '0.15em', margin: '0 0 15px',
        }}>Le Cabinet</h1>
        <p style={{
          fontFamily: 'var(--font-sans-body)', color: 'var(--color-text-on-dark)', opacity: 0.7,
          maxWidth: 500, margin: '0 auto 10px', lineHeight: 1.7,
        }}>Iris a rassemblé ici ce qu'elle ne montre qu'à ceux qui poussent la porte.</p>
        <p style={{
          fontFamily: 'var(--font-sans-body)', fontSize: 13, color: 'var(--color-text-on-dark)',
          opacity: 0.7, margin: '0 auto 30px',
        }}>En entrant, vous confirmez avoir plus de 18 ans.</p>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22 }}>
          <Button variant="primary" onClick={() => go('cabinet')}>Entrer</Button>
          <Button variant="ghost" onClick={() => go('home')}>Retourner à la Vitrine</Button>
        </div>
      </div>
    </section>
  );
}

// ── Le Cabinet (univers niveau 2) ─────────────────────────
function CabinetPage({ go }) {
  const { CategoryTile, IrisQuote } = DS_screens;
  return (
    <div style={{ background: 'var(--color-primary)' }}>
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '54px 40px 60px' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{
            fontFamily: 'var(--font-serif-display)', fontWeight: 400, fontSize: '2.2rem',
            letterSpacing: '0.15em', color: 'var(--color-text-on-dark)', margin: '0 0 8px',
          }}>Le Cabinet</h1>
          <p style={{
            fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 13,
            letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--color-accent)', margin: 0,
          }}>Six pièces, six curiosités</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18 }}>
          {CABINET_CATEGORIES.map((c) => (
            <CategoryTile key={c.name} name={c.name} description={c.desc} tone="cabinet" height={190}
              onClick={() => CATALOG[c.name] ? go('category', { category: c.name }) : null} />
          ))}
        </div>
      </section>
      <IrisQuote>On ne force jamais une porte. On la pousse.</IrisQuote>
      <div style={{ height: 40 }}></div>
    </div>
  );
}

Object.assign(window, { HomePage, GatePage, CabinetPage, CarnetCard });

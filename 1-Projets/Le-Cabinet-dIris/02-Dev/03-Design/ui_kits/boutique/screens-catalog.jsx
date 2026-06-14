// Écrans catalogue — catégorie + fiche produit
const DS_catalog = window.LeCabinetDIrisDesignSystem_55ae4c;

// ── Page catégorie ────────────────────────────────────────
function CategoryPage({ go, category }) {
  const { EditorialText, ProductCard } = DS_catalog;
  const data = CATALOG[category] || { intro: '', products: [], tone: 'vitrine' };
  const isCabinet = data.tone === 'cabinet';
  return (
    <div style={isCabinet ? { background: 'var(--color-background-dark)' } : {}}>
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '46px 40px 70px' }}>
        <div style={{ textAlign: 'center', marginBottom: 26 }}>
          {isCabinet ? (
            <span style={{
              fontFamily: 'var(--font-sans-body)', fontSize: 11, textTransform: 'uppercase',
              letterSpacing: '0.1em', padding: '4px 12px', borderRadius: 1,
              background: 'var(--color-cabinet)', color: 'var(--color-text-on-dark)',
              display: 'inline-block', marginBottom: 14,
            }}>Cabinet</span>
          ) : null}
          <h1 style={{
            fontFamily: 'var(--font-serif-display)', fontWeight: 600, fontSize: '2rem',
            letterSpacing: '0.04em', color: 'var(--color-primary)', margin: 0,
          }}>{category}</h1>
        </div>
        <EditorialText>{data.intro}</EditorialText>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18, marginTop: 44 }}>
          {data.products.map((p) => (
            <ProductCard key={p.name} {...p} onClick={() => go('product', { product: p, category })} />
          ))}
        </div>
      </section>
    </div>
  );
}

// ── Fiche produit ─────────────────────────────────────────
function ProductPage({ go, product, category, onAddToCart }) {
  const { Button, Badge, PriceTag, Separator } = DS_catalog;
  const [added, setAdded] = React.useState(false);
  const isCabinet = product.badge === 'cabinet';
  const add = () => { setAdded(true); onAddToCart(); setTimeout(() => setAdded(false), 1800); };
  return (
    <section style={{ maxWidth: 1000, margin: '0 auto', padding: '50px 40px 80px' }}>
      <a onClick={() => go('category', { category })} style={{
        fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 12.5,
        letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--color-text-secondary)',
        cursor: 'pointer', display: 'inline-block', marginBottom: 30, textDecoration: 'none',
      }}>← {category}</a>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 56, alignItems: 'start' }}>
        {/* Image encadrée passe-partout */}
        <div style={{ border: '0.5px solid var(--color-border-strong)', padding: 8, background: 'var(--color-background)' }}>
          <div style={{
            aspectRatio: '3 / 4', background: 'var(--color-background-dark)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{
              fontFamily: 'var(--font-serif-display)', fontSize: 44, color: 'var(--color-border)',
              border: '1px solid var(--color-border)', borderRadius: '50%', width: 76, height: 98,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>I</span>
          </div>
        </div>
        <div>
          <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
            {product.badge === 'rare' ? <Badge variant="rare" /> : null}
            {isCabinet ? <Badge variant="cabinet" /> : null}
          </div>
          <h1 style={{
            fontFamily: 'var(--font-serif-display)', fontSize: '1.8rem', fontWeight: 600,
            color: 'var(--color-primary)', margin: '0 0 8px', letterSpacing: '0.02em',
          }}>{product.name}</h1>
          <PriceTag amount={product.price} size="lg" />
          <p style={{
            fontFamily: 'var(--font-sans-body)', lineHeight: 1.8, color: 'var(--color-text-secondary)',
            margin: '22px 0 30px', maxWidth: 420,
          }}>
            Iris l'a choisie pour ce qu'elle promet sans le dire. Chaque pièce est inspectée,
            enveloppée de papier de soie et scellée à la maison — l'écrin ne dit rien de ce qu'il contient.
          </p>
          <Button variant="primary" onClick={add}>{added ? 'Ajouté à l\u2019écrin' : 'Ajouter au panier'}</Button>
          <div style={{ margin: '34px 0 0', maxWidth: 420 }}>
            <Separator />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 18 }}>
              <DetailRow label="Livraison">Colis neutre, sous 3 à 5 jours</DetailRow>
              <DetailRow label="Retours">14 jours, sans question</DetailRow>
              <DetailRow label="Discrétion">Libellé bancaire anonyme</DetailRow>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function DetailRow({ label, children }) {
  return (
    <div style={{ display: 'flex', gap: 14, alignItems: 'baseline' }}>
      <span style={{
        fontFamily: 'var(--font-sans-body)', fontWeight: 700, fontSize: 11,
        letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--color-accent-dark)', minWidth: 90,
      }}>{label}</span>
      <span style={{ fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 13.5, color: 'var(--color-text-secondary)' }}>{children}</span>
    </div>
  );
}

Object.assign(window, { CategoryPage, ProductPage, DetailRow });

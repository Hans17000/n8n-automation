// Header + Footer — Le Cabinet d'Iris
const DS_chrome = window.LeCabinetDIrisDesignSystem_55ae4c;

const VITRINE_NAV = ['Les Étoffes', 'Les Nuits', 'Les Voiles', 'Les Élixirs', 'Les Écrins'];

function NavLink({ children, onClick, active }) {
  const [hover, setHover] = React.useState(false);
  return (
    <a
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        fontFamily: 'var(--font-serif-display)', fontWeight: 400, fontSize: 13,
        textTransform: 'uppercase', letterSpacing: '0.15em', textDecoration: 'none',
        color: hover || active ? 'var(--color-accent)' : 'var(--color-text-on-dark)',
        transition: 'color 0.3s ease', cursor: 'pointer', whiteSpace: 'nowrap',
      }}
    >
      {children}
    </a>
  );
}

function Header({ go, route, cartCount }) {
  const { Button } = DS_chrome;
  return (
    <header style={{ background: 'var(--color-primary)', borderBottom: '1px solid var(--color-accent)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 40px 12px' }}>
        <div style={{ width: 120 }}></div>
        <div onClick={() => go('home')} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
          <span style={{
            width: 34, height: 44, border: '1px solid var(--color-accent)', borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-serif-display)', fontSize: 21, color: 'var(--color-accent)',
          }}>I</span>
          <span style={{
            fontFamily: 'var(--font-serif-display)', fontWeight: 400, fontSize: 17,
            letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--color-text-on-dark)',
          }}>Le Cabinet d'Iris</span>
        </div>
        <div style={{ width: 120, display: 'flex', justifyContent: 'flex-end', gap: 18, color: 'var(--color-accent)' }}>
          <span style={{ cursor: 'pointer' }}><IconSearch /></span>
          <span style={{ cursor: 'pointer' }}><IconUser /></span>
          <span style={{ cursor: 'pointer', position: 'relative' }}>
            <IconBag />
            {cartCount > 0 ? (
              <span style={{
                position: 'absolute', top: -6, right: -8, background: 'var(--color-alert)',
                color: 'var(--color-text-on-dark)', fontFamily: 'var(--font-sans-body)',
                fontSize: 10, lineHeight: 1, padding: '3px 5px', borderRadius: 1,
              }}>{cartCount}</span>
            ) : null}
          </span>
        </div>
      </div>
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 26, padding: '10px 40px 16px' }}>
        {VITRINE_NAV.map((c) => (
          <NavLink key={c} active={route.name === 'category' && route.category === c} onClick={() => go('category', { category: c })}>{c}</NavLink>
        ))}
        <span style={{ display: 'inline-block', width: 1, height: 20, background: 'var(--color-accent)', margin: '0 6px' }}></span>
        <Button variant="cabinet-entry" onClick={() => go('gate')}>Poussez la porte</Button>
      </nav>
    </header>
  );
}

function Footer() {
  const { ReassuranceItem, Separator } = DS_chrome;
  const cols = {
    'La Maison': ['Qui est Iris ?', 'Les Carnets d\u2019Iris', 'Nous écrire'],
    'Vos emplettes': ['Livraison & retours', 'Paiement', 'Conditions générales'],
    'Discrétion': ['Confidentialité', 'Emballage neutre', 'Cookies'],
  };
  const FooterLink = ({ children }) => {
    const [hover, setHover] = React.useState(false);
    return (
      <a onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
        style={{
          fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 13,
          color: hover ? 'var(--color-accent)' : 'var(--color-text-on-dark)',
          opacity: hover ? 1 : 0.7, transition: 'opacity 0.3s ease, color 0.3s ease',
          textDecoration: 'none', cursor: 'pointer',
        }}>{children}</a>
    );
  };
  return (
    <footer style={{ background: 'var(--color-primary)', borderTop: '1px solid var(--color-accent)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', padding: '34px 60px 26px', maxWidth: 1100, margin: '0 auto' }}>
        <ReassuranceItem icon={<IconPackage />} label="Livraison discrète" />
        <ReassuranceItem icon={<IconLock />} label="Paiement sécurisé" />
        <ReassuranceItem icon={<IconKey />} label="Curation Iris" />
        <ReassuranceItem icon={<IconUndo />} label="Retours sous 14j" />
      </div>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 60px' }}><Separator motif="❦" /></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 40, maxWidth: 900, margin: '0 auto', padding: '30px 60px 40px' }}>
        {Object.entries(cols).map(([title, links]) => (
          <div key={title} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <h4 style={{
              fontFamily: 'var(--font-serif-display)', fontWeight: 400, textTransform: 'uppercase',
              letterSpacing: '0.1em', color: 'var(--color-accent)', fontSize: 14, margin: '0 0 6px',
            }}>{title}</h4>
            {links.map((l) => <FooterLink key={l}>{l}</FooterLink>)}
          </div>
        ))}
      </div>
      <p style={{
        textAlign: 'center', fontFamily: 'var(--font-sans-body)', fontWeight: 300, fontSize: 11,
        letterSpacing: '0.1em', color: 'var(--color-text-on-dark)', opacity: 0.4, padding: '0 0 24px', margin: 0,
      }}>© 2026 Le Cabinet d'Iris — Réservé aux personnes majeures</p>
    </footer>
  );
}

Object.assign(window, { Header, Footer, VITRINE_NAV });

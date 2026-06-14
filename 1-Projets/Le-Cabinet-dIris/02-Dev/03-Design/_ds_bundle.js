/* @ds-bundle: {"format":3,"namespace":"LeCabinetDIrisDesignSystem_55ae4c","components":[{"name":"CategoryTile","sourcePath":"components/commerce/CategoryTile.jsx"},{"name":"ProductCard","sourcePath":"components/commerce/ProductCard.jsx"},{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"EditorialText","sourcePath":"components/core/EditorialText.jsx"},{"name":"IrisQuote","sourcePath":"components/core/IrisQuote.jsx"},{"name":"PriceTag","sourcePath":"components/core/PriceTag.jsx"},{"name":"ReassuranceItem","sourcePath":"components/core/ReassuranceItem.jsx"},{"name":"SectionTitle","sourcePath":"components/core/SectionTitle.jsx"},{"name":"Separator","sourcePath":"components/core/Separator.jsx"}],"sourceHashes":{"components/commerce/CategoryTile.jsx":"4bfb55907888","components/commerce/ProductCard.jsx":"eae5eddf1c2f","components/core/Badge.jsx":"814783b2eeb4","components/core/Button.jsx":"200f5402592e","components/core/EditorialText.jsx":"132f0c8237bd","components/core/IrisQuote.jsx":"2148b1b320e4","components/core/PriceTag.jsx":"bfaafb86c4b0","components/core/ReassuranceItem.jsx":"3972022ce9a2","components/core/SectionTitle.jsx":"34e0b3c35975","components/core/Separator.jsx":"601696f6aa1b","ui_kits/boutique/chrome.jsx":"94ce23dd096f","ui_kits/boutique/data.jsx":"3291e09bfe79","ui_kits/boutique/icons.jsx":"ba6f29de0a73","ui_kits/boutique/screens-catalog.jsx":"37723bd0c024","ui_kits/boutique/screens-home.jsx":"08c37d28c170"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.LeCabinetDIrisDesignSystem_55ae4c = window.LeCabinetDIrisDesignSystem_55ae4c || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/commerce/CategoryTile.jsx
try { (() => {
/**
 * Tuile d'univers / catégorie — fond sombre (encre ou prune), nom serif, sous-texte.
 */
function CategoryTile({
  name,
  description,
  tone = 'vitrine',
  onClick,
  height = 220
}) {
  const [hover, setHover] = React.useState(false);
  const bg = tone === 'cabinet' ? 'var(--color-cabinet)' : 'var(--color-primary)';
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
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
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 400,
      fontSize: 24,
      letterSpacing: '0.08em',
      color: 'var(--color-text-on-dark)',
      margin: 0
    }
  }, name), description ? /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontStyle: 'italic',
      fontSize: 13,
      color: 'var(--color-accent-light)',
      margin: 0,
      maxWidth: 260,
      lineHeight: 1.6
    }
  }, description) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: 12,
      textTransform: 'uppercase',
      letterSpacing: '0.15em',
      color: 'var(--color-accent)',
      borderBottom: `1px solid ${hover ? 'var(--color-accent)' : 'transparent'}`,
      transition: 'border-color 0.3s ease',
      marginTop: 6
    }
  }, "D\xE9couvrir"));
}
Object.assign(__ds_scope, { CategoryTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/commerce/CategoryTile.jsx", error: String((e && e.message) || e) }); }

// components/core/Badge.jsx
try { (() => {
/**
 * Badge produit : « Pièce rare » (bordeaux, bord doré) ou « Cabinet » (prune).
 */
function Badge({
  variant = 'rare',
  children
}) {
  const styles = {
    rare: {
      backgroundColor: 'var(--color-alert)',
      border: '0.5px solid var(--color-border-strong)'
    },
    cabinet: {
      backgroundColor: 'var(--color-cabinet)',
      border: 'none'
    }
  };
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-block',
      fontFamily: 'var(--font-sans-body)',
      fontSize: 11,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
      padding: '4px 12px',
      borderRadius: 1,
      color: 'var(--color-text-on-dark)',
      ...styles[variant]
    }
  }, children || (variant === 'rare' ? 'Pièce rare' : 'Cabinet'));
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
/**
 * Bouton Le Cabinet d'Iris.
 * variant: 'primary' (fond or) | 'secondary' (outline or) | 'cabinet-entry' (italique, « Poussez la porte ») | 'ghost' (lien souligné discret)
 */
function Button({
  variant = 'primary',
  children,
  href,
  onClick,
  disabled = false,
  style
}) {
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
    pointerEvents: disabled ? 'none' : 'auto'
  };
  const variants = {
    primary: {
      backgroundColor: hover ? 'var(--color-btn-primary-hover)' : 'var(--color-btn-primary-bg)',
      color: 'var(--color-btn-primary-text)',
      border: 'none',
      padding: '14px 40px'
    },
    secondary: {
      backgroundColor: hover ? 'var(--color-accent)' : 'transparent',
      color: hover ? 'var(--color-primary)' : 'var(--color-btn-secondary-text)',
      border: '1px solid var(--color-btn-secondary-border)',
      padding: '12px 40px',
      letterSpacing: '0.15em'
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
      fontSize: 15
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
      opacity: disabled ? 0.4 : hover ? 0.9 : 0.5
    }
  };
  const Tag = href ? 'a' : 'button';
  return /*#__PURE__*/React.createElement(Tag, {
    href: href,
    onClick: onClick,
    disabled: disabled,
    style: {
      ...base,
      ...variants[variant],
      ...style
    },
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false)
  }, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/EditorialText.jsx
try { (() => {
/**
 * Texte éditorial de catégorie — italique centré entre deux filets dorés, max 700px.
 */
function EditorialText({
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
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
      borderBottom: '1px solid var(--color-border)'
    }
  }, children);
}
Object.assign(__ds_scope, { EditorialText });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/EditorialText.jsx", error: String((e && e.message) || e) }); }

// components/core/IrisQuote.jsx
try { (() => {
/**
 * Citation d'Iris — Pinyon Script sur fond sombre, guillemets dorés.
 */
function IrisQuote({
  children,
  attribution = 'Iris'
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      padding: '30px 20px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: 32,
      color: 'var(--color-accent)',
      lineHeight: 1,
      display: 'block',
      marginBottom: 4
    }
  }, "\xAB"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-script)',
      fontSize: 'var(--text-quote, 20px)',
      color: 'var(--color-text-on-dark)',
      margin: 0,
      maxWidth: 500,
      marginLeft: 'auto',
      marginRight: 'auto'
    }
  }, children), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 11,
      letterSpacing: '0.2em',
      textTransform: 'uppercase',
      color: 'var(--color-accent)',
      display: 'block',
      marginTop: 10
    }
  }, attribution));
}
Object.assign(__ds_scope, { IrisQuote });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/IrisQuote.jsx", error: String((e && e.message) || e) }); }

// components/core/PriceTag.jsx
try { (() => {
/**
 * Prix — Lato Light 300 doré, letter-spacing 0.05em.
 */
function PriceTag({
  amount,
  size = 'md',
  currency = '€'
}) {
  const sizes = {
    sm: 14,
    md: 16,
    lg: '1.6rem'
  };
  const formatted = typeof amount === 'number' ? amount.toFixed(2).replace('.', ',') : amount;
  return /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: sizes[size],
      color: 'var(--color-accent)',
      letterSpacing: '0.05em'
    }
  }, formatted, "\xA0", currency);
}
Object.assign(__ds_scope, { PriceTag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/PriceTag.jsx", error: String((e && e.message) || e) }); }

// components/commerce/ProductCard.jsx
try { (() => {
/**
 * Miniature produit — fond ivoire, hairline dorée, bordure or plein au hover.
 */
function ProductCard({
  name,
  price,
  image,
  badge,
  category,
  onClick
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      background: 'var(--color-background)',
      border: `0.5px solid ${hover ? 'var(--color-accent)' : 'var(--color-border)'}`,
      transition: 'border-color 0.3s ease',
      cursor: onClick ? 'pointer' : 'default',
      position: 'relative'
    }
  }, badge ? /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      top: 10,
      left: 10,
      zIndex: 1
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Badge, {
    variant: badge
  })) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      aspectRatio: '3 / 4',
      background: 'var(--color-background-dark)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden'
    }
  }, image ? /*#__PURE__*/React.createElement("img", {
    src: image,
    alt: name,
    style: {
      width: '100%',
      height: '100%',
      objectFit: 'cover'
    }
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: 28,
      color: 'var(--color-border)',
      border: '1px solid var(--color-border)',
      borderRadius: '50%',
      width: 48,
      height: 62,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, "I")), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '14px 16px 18px',
      textAlign: 'center'
    }
  }, category ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 10.5,
      letterSpacing: '0.15em',
      textTransform: 'uppercase',
      color: 'var(--color-text-secondary)',
      display: 'block',
      marginBottom: 4
    }
  }, category) : null, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 600,
      fontSize: 17,
      letterSpacing: '0.02em',
      color: 'var(--color-primary)',
      margin: '0 0 6px'
    }
  }, name), /*#__PURE__*/React.createElement(__ds_scope.PriceTag, {
    amount: price
  })));
}
Object.assign(__ds_scope, { ProductCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/commerce/ProductCard.jsx", error: String((e && e.message) || e) }); }

// components/core/ReassuranceItem.jsx
try { (() => {
/**
 * Bloc de réassurance — icône trait or + libellé ivoire, sur fond noir d'encre.
 * Icône : passer un nœud React (ex. SVG Lucide inline) via `icon`.
 */
function ReassuranceItem({
  icon,
  label
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 10,
      textAlign: 'center',
      padding: 10,
      color: 'var(--color-accent)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 26,
      height: 26,
      display: 'block'
    }
  }, icon), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 12,
      letterSpacing: '0.08em',
      color: 'var(--color-text-on-dark)'
    }
  }, label));
}
Object.assign(__ds_scope, { ReassuranceItem });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/ReassuranceItem.jsx", error: String((e && e.message) || e) }); }

// components/core/SectionTitle.jsx
try { (() => {
/**
 * Titre de section centré avec filets dorés latéraux (« Sélection d'Iris »).
 */
function SectionTitle({
  children,
  subtitle,
  onDark = false
}) {
  const lineStyle = {
    flex: 1,
    height: 1,
    background: 'var(--color-border)',
    maxWidth: 120
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      margin: '0 auto'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: lineStyle
  }), /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 600,
      fontSize: '1.6rem',
      letterSpacing: '0.06em',
      color: onDark ? 'var(--color-text-on-dark)' : 'var(--color-primary)',
      margin: 0,
      whiteSpace: 'nowrap'
    }
  }, children), /*#__PURE__*/React.createElement("div", {
    style: lineStyle
  })), subtitle ? /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 13,
      letterSpacing: '0.2em',
      textTransform: 'uppercase',
      color: 'var(--color-accent)',
      margin: '10px 0 0'
    }
  }, subtitle) : null);
}
Object.assign(__ds_scope, { SectionTitle });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/SectionTitle.jsx", error: String((e && e.message) || e) }); }

// components/core/Separator.jsx
try { (() => {
/**
 * Séparateur — filet doré avec motif central (monogramme « I » ou fleuron).
 */
function Separator({
  motif = 'I',
  onDark = false,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      height: 1,
      background: 'var(--color-border)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: 16,
      lineHeight: 1,
      color: 'var(--color-accent)'
    }
  }, motif), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      height: 1,
      background: 'var(--color-border)'
    }
  }));
}
Object.assign(__ds_scope, { Separator });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Separator.jsx", error: String((e && e.message) || e) }); }

// ui_kits/boutique/chrome.jsx
try { (() => {
// Header + Footer — Le Cabinet d'Iris
const DS_chrome = window.LeCabinetDIrisDesignSystem_55ae4c;
const VITRINE_NAV = ['Les Étoffes', 'Les Nuits', 'Les Voiles', 'Les Élixirs', 'Les Écrins'];
function NavLink({
  children,
  onClick,
  active
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("a", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 400,
      fontSize: 13,
      textTransform: 'uppercase',
      letterSpacing: '0.15em',
      textDecoration: 'none',
      color: hover || active ? 'var(--color-accent)' : 'var(--color-text-on-dark)',
      transition: 'color 0.3s ease',
      cursor: 'pointer',
      whiteSpace: 'nowrap'
    }
  }, children);
}
function Header({
  go,
  route,
  cartCount
}) {
  const {
    Button
  } = DS_chrome;
  return /*#__PURE__*/React.createElement("header", {
    style: {
      background: 'var(--color-primary)',
      borderBottom: '1px solid var(--color-accent)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 40px 12px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 120
    }
  }), /*#__PURE__*/React.createElement("div", {
    onClick: () => go('home'),
    style: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 4,
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 34,
      height: 44,
      border: '1px solid var(--color-accent)',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'var(--font-serif-display)',
      fontSize: 21,
      color: 'var(--color-accent)'
    }
  }, "I"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 400,
      fontSize: 17,
      letterSpacing: '0.18em',
      textTransform: 'uppercase',
      color: 'var(--color-text-on-dark)'
    }
  }, "Le Cabinet d'Iris")), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 120,
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 18,
      color: 'var(--color-accent)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement(IconSearch, null)), /*#__PURE__*/React.createElement("span", {
    style: {
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement(IconUser, null)), /*#__PURE__*/React.createElement("span", {
    style: {
      cursor: 'pointer',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement(IconBag, null), cartCount > 0 ? /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      top: -6,
      right: -8,
      background: 'var(--color-alert)',
      color: 'var(--color-text-on-dark)',
      fontFamily: 'var(--font-sans-body)',
      fontSize: 10,
      lineHeight: 1,
      padding: '3px 5px',
      borderRadius: 1
    }
  }, cartCount) : null))), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 26,
      padding: '10px 40px 16px'
    }
  }, VITRINE_NAV.map(c => /*#__PURE__*/React.createElement(NavLink, {
    key: c,
    active: route.name === 'category' && route.category === c,
    onClick: () => go('category', {
      category: c
    })
  }, c)), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-block',
      width: 1,
      height: 20,
      background: 'var(--color-accent)',
      margin: '0 6px'
    }
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "cabinet-entry",
    onClick: () => go('gate')
  }, "Poussez la porte")));
}
function Footer() {
  const {
    ReassuranceItem,
    Separator
  } = DS_chrome;
  const cols = {
    'La Maison': ['Qui est Iris ?', 'Les Carnets d\u2019Iris', 'Nous écrire'],
    'Vos emplettes': ['Livraison & retours', 'Paiement', 'Conditions générales'],
    'Discrétion': ['Confidentialité', 'Emballage neutre', 'Cookies']
  };
  const FooterLink = ({
    children
  }) => {
    const [hover, setHover] = React.useState(false);
    return /*#__PURE__*/React.createElement("a", {
      onMouseEnter: () => setHover(true),
      onMouseLeave: () => setHover(false),
      style: {
        fontFamily: 'var(--font-sans-body)',
        fontWeight: 300,
        fontSize: 13,
        color: hover ? 'var(--color-accent)' : 'var(--color-text-on-dark)',
        opacity: hover ? 1 : 0.7,
        transition: 'opacity 0.3s ease, color 0.3s ease',
        textDecoration: 'none',
        cursor: 'pointer'
      }
    }, children);
  };
  return /*#__PURE__*/React.createElement("footer", {
    style: {
      background: 'var(--color-primary)',
      borderTop: '1px solid var(--color-accent)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      padding: '34px 60px 26px',
      maxWidth: 1100,
      margin: '0 auto'
    }
  }, /*#__PURE__*/React.createElement(ReassuranceItem, {
    icon: /*#__PURE__*/React.createElement(IconPackage, null),
    label: "Livraison discr\xE8te"
  }), /*#__PURE__*/React.createElement(ReassuranceItem, {
    icon: /*#__PURE__*/React.createElement(IconLock, null),
    label: "Paiement s\xE9curis\xE9"
  }), /*#__PURE__*/React.createElement(ReassuranceItem, {
    icon: /*#__PURE__*/React.createElement(IconKey, null),
    label: "Curation Iris"
  }), /*#__PURE__*/React.createElement(ReassuranceItem, {
    icon: /*#__PURE__*/React.createElement(IconUndo, null),
    label: "Retours sous 14j"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '0 60px'
    }
  }, /*#__PURE__*/React.createElement(Separator, {
    motif: "\u2766"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 40,
      maxWidth: 900,
      margin: '0 auto',
      padding: '30px 60px 40px'
    }
  }, Object.entries(cols).map(([title, links]) => /*#__PURE__*/React.createElement("div", {
    key: title,
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 400,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
      color: 'var(--color-accent)',
      fontSize: 14,
      margin: '0 0 6px'
    }
  }, title), links.map(l => /*#__PURE__*/React.createElement(FooterLink, {
    key: l
  }, l))))), /*#__PURE__*/React.createElement("p", {
    style: {
      textAlign: 'center',
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 11,
      letterSpacing: '0.1em',
      color: 'var(--color-text-on-dark)',
      opacity: 0.4,
      padding: '0 0 24px',
      margin: 0
    }
  }, "\xA9 2026 Le Cabinet d'Iris \u2014 R\xE9serv\xE9 aux personnes majeures"));
}
Object.assign(window, {
  Header,
  Footer,
  VITRINE_NAV
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/boutique/chrome.jsx", error: String((e && e.message) || e) }); }

// ui_kits/boutique/data.jsx
try { (() => {
// Données de démonstration — Le Cabinet d'Iris
const CATALOG = {
  'Les Étoffes': {
    tone: 'vitrine',
    intro: 'La dentelle est une écriture. Iris a réuni ici les étoffes qui se lisent du bout des doigts — guipures, tulles et soies qui promettent sans jamais tout dire.',
    products: [{
      name: 'Soutien-gorge Aurore',
      price: 89
    }, {
      name: 'Culotte Héloïse',
      price: 45
    }, {
      name: 'Body Insomnie',
      price: 125,
      badge: 'rare'
    }, {
      name: 'Guêpière Comtesse',
      price: 160
    }, {
      name: 'Porte-jarretelles Minuit',
      price: 65
    }, {
      name: 'Caraco Aube Pâle',
      price: 78
    }]
  },
  'Les Nuits': {
    tone: 'vitrine',
    intro: 'Ce que l\u2019on porte quand on ne porte presque rien. Nuisettes et kimonos pour les heures où la maison se tait.',
    products: [{
      name: 'Nuisette Minuit',
      price: 145,
      badge: 'rare'
    }, {
      name: 'Kimono Songe',
      price: 190
    }, {
      name: 'Nuisette Velours d\u2019Ombre',
      price: 130
    }, {
      name: 'Pyjama Confidence',
      price: 110
    }]
  },
  'Les Voiles': {
    tone: 'vitrine',
    intro: 'Des transparences qui voilent mieux qu\u2019elles ne dévoilent.',
    products: [{
      name: 'Peignoir Brume',
      price: 95
    }, {
      name: 'Robe d\u2019intérieur Solstice',
      price: 175
    }, {
      name: 'Voile Équivoque',
      price: 85
    }]
  },
  'Les Élixirs': {
    tone: 'vitrine',
    intro: 'Huiles, baumes et parfums d\u2019alcôve — la chimie discrète des soirs choisis.',
    products: [{
      name: 'Huile Lueur',
      price: 38
    }, {
      name: 'Baume Avant-Nuit',
      price: 29
    }, {
      name: 'Brume d\u2019Oreiller №3',
      price: 42,
      badge: 'rare'
    }, {
      name: 'Bougie de Massage Cire Douce',
      price: 35
    }]
  },
  'Les Écrins': {
    tone: 'vitrine',
    intro: 'Coffrets composés par Iris — pour offrir sans expliquer.',
    products: [{
      name: 'Écrin Première Fois',
      price: 120
    }, {
      name: 'Écrin Anniversaire',
      price: 180
    }, {
      name: 'Écrin Carte Blanche',
      price: 250,
      badge: 'rare'
    }]
  },
  'Les Apparitions': {
    tone: 'cabinet',
    intro: 'Tenues qui n\u2019existent que le temps d\u2019une apparition.',
    products: [{
      name: 'Harnais Dentelle Noire',
      price: 95,
      badge: 'cabinet'
    }, {
      name: 'Cape Équinoxe',
      price: 210,
      badge: 'cabinet'
    }, {
      name: 'Masque Vénitien Or Mat',
      price: 75,
      badge: 'cabinet'
    }]
  },
  'Le Boudoir Noir': {
    tone: 'cabinet',
    intro: 'Le velours a ses raisons. Pièces choisies pour qui sait demander.',
    products: [{
      name: 'Cravache Velours',
      price: 120,
      badge: 'cabinet'
    }, {
      name: 'Menottes Soie & Laiton',
      price: 85,
      badge: 'cabinet'
    }, {
      name: 'Flogger Cuir Patiné',
      price: 140,
      badge: 'rare'
    }, {
      name: 'Bandeau Nuit Close',
      price: 48,
      badge: 'cabinet'
    }]
  }
};
const CABINET_CATEGORIES = [{
  name: 'Les Apparitions',
  desc: 'Tenues qui n\u2019existent que le temps d\u2019une apparition.'
}, {
  name: 'Les Objets',
  desc: 'Curiosités de design, à poser ou à cacher.'
}, {
  name: 'Les Confessions',
  desc: 'Ce qui se murmure entre initiés.'
}, {
  name: 'Les Complicités',
  desc: 'À deux, ou davantage.'
}, {
  name: 'Le Boudoir Noir',
  desc: 'Le velours a ses raisons.'
}, {
  name: 'Les Caprices',
  desc: 'Les envies qui ne s\u2019expliquent pas.'
}];
const HOME_SELECTION = [{
  name: 'Body Insomnie',
  price: 125,
  category: 'Les Étoffes',
  badge: 'rare'
}, {
  name: 'Nuisette Minuit',
  price: 145,
  category: 'Les Nuits'
}, {
  name: 'Brume d\u2019Oreiller №3',
  price: 42,
  category: 'Les Élixirs'
}, {
  name: 'Écrin Carte Blanche',
  price: 250,
  category: 'Les Écrins',
  badge: 'rare'
}];
const CARNETS = [{
  title: 'L\u2019art de recevoir sans rien montrer',
  date: '12 mai 2026'
}, {
  title: 'Petite grammaire de la dentelle',
  date: '28 avril 2026'
}, {
  title: 'Du bon usage des clés anciennes',
  date: '9 avril 2026'
}];
Object.assign(window, {
  CATALOG,
  CABINET_CATEGORIES,
  HOME_SELECTION,
  CARNETS
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/boutique/data.jsx", error: String((e && e.message) || e) }); }

// ui_kits/boutique/icons.jsx
try { (() => {
// Icônes Lucide inline (trait 1.5, currentColor) — substitution flaguée dans readme.md
const iSvg = (paths, size = 20) => props => /*#__PURE__*/React.createElement("svg", {
  xmlns: "http://www.w3.org/2000/svg",
  width: props && props.size || size,
  height: props && props.size || size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "1.5",
  strokeLinecap: "round",
  strokeLinejoin: "round",
  dangerouslySetInnerHTML: {
    __html: paths
  }
});
const IconSearch = iSvg('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>');
const IconUser = iSvg('<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>');
const IconBag = iSvg('<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>');
const IconPackage = iSvg('<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>', 26);
const IconLock = iSvg('<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>', 26);
const IconKey = iSvg('<path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/>', 26);
const IconUndo = iSvg('<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5a5.5 5.5 0 0 1-5.5 5.5H11"/>', 26);
const IconFeather = iSvg('<path d="M12.67 19a2 2 0 0 0 1.416-.588l6.154-6.172a6 6 0 0 0-8.49-8.49L5.586 9.914A2 2 0 0 0 5 11.328V18a1 1 0 0 0 1 1z"/><path d="M16 8 2 22"/><path d="M17.5 15H9"/>', 26);
Object.assign(window, {
  IconSearch,
  IconUser,
  IconBag,
  IconPackage,
  IconLock,
  IconKey,
  IconUndo,
  IconFeather
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/boutique/icons.jsx", error: String((e && e.message) || e) }); }

// ui_kits/boutique/screens-catalog.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
// Écrans catalogue — catégorie + fiche produit
const DS_catalog = window.LeCabinetDIrisDesignSystem_55ae4c;

// ── Page catégorie ────────────────────────────────────────
function CategoryPage({
  go,
  category
}) {
  const {
    EditorialText,
    ProductCard
  } = DS_catalog;
  const data = CATALOG[category] || {
    intro: '',
    products: [],
    tone: 'vitrine'
  };
  const isCabinet = data.tone === 'cabinet';
  return /*#__PURE__*/React.createElement("div", {
    style: isCabinet ? {
      background: 'var(--color-background-dark)'
    } : {}
  }, /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '46px 40px 70px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      marginBottom: 26
    }
  }, isCabinet ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontSize: 11,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
      padding: '4px 12px',
      borderRadius: 1,
      background: 'var(--color-cabinet)',
      color: 'var(--color-text-on-dark)',
      display: 'inline-block',
      marginBottom: 14
    }
  }, "Cabinet") : null, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 600,
      fontSize: '2rem',
      letterSpacing: '0.04em',
      color: 'var(--color-primary)',
      margin: 0
    }
  }, category)), /*#__PURE__*/React.createElement(EditorialText, null, data.intro), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 18,
      marginTop: 44
    }
  }, data.products.map(p => /*#__PURE__*/React.createElement(ProductCard, _extends({
    key: p.name
  }, p, {
    onClick: () => go('product', {
      product: p,
      category
    })
  }))))));
}

// ── Fiche produit ─────────────────────────────────────────
function ProductPage({
  go,
  product,
  category,
  onAddToCart
}) {
  const {
    Button,
    Badge,
    PriceTag,
    Separator
  } = DS_catalog;
  const [added, setAdded] = React.useState(false);
  const isCabinet = product.badge === 'cabinet';
  const add = () => {
    setAdded(true);
    onAddToCart();
    setTimeout(() => setAdded(false), 1800);
  };
  return /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1000,
      margin: '0 auto',
      padding: '50px 40px 80px'
    }
  }, /*#__PURE__*/React.createElement("a", {
    onClick: () => go('category', {
      category
    }),
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 12.5,
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
      color: 'var(--color-text-secondary)',
      cursor: 'pointer',
      display: 'inline-block',
      marginBottom: 30,
      textDecoration: 'none'
    }
  }, "\u2190 ", category), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 56,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      border: '0.5px solid var(--color-border-strong)',
      padding: 8,
      background: 'var(--color-background)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      aspectRatio: '3 / 4',
      background: 'var(--color-background-dark)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: 44,
      color: 'var(--color-border)',
      border: '1px solid var(--color-border)',
      borderRadius: '50%',
      width: 76,
      height: 98,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, "I"))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      marginBottom: 16
    }
  }, product.badge === 'rare' ? /*#__PURE__*/React.createElement(Badge, {
    variant: "rare"
  }) : null, isCabinet ? /*#__PURE__*/React.createElement(Badge, {
    variant: "cabinet"
  }) : null), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: '1.8rem',
      fontWeight: 600,
      color: 'var(--color-primary)',
      margin: '0 0 8px',
      letterSpacing: '0.02em'
    }
  }, product.name), /*#__PURE__*/React.createElement(PriceTag, {
    amount: product.price,
    size: "lg"
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      lineHeight: 1.8,
      color: 'var(--color-text-secondary)',
      margin: '22px 0 30px',
      maxWidth: 420
    }
  }, "Iris l'a choisie pour ce qu'elle promet sans le dire. Chaque pi\xE8ce est inspect\xE9e, envelopp\xE9e de papier de soie et scell\xE9e \xE0 la maison \u2014 l'\xE9crin ne dit rien de ce qu'il contient."), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    onClick: add
  }, added ? 'Ajouté à l\u2019écrin' : 'Ajouter au panier'), /*#__PURE__*/React.createElement("div", {
    style: {
      margin: '34px 0 0',
      maxWidth: 420
    }
  }, /*#__PURE__*/React.createElement(Separator, null), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      marginTop: 18
    }
  }, /*#__PURE__*/React.createElement(DetailRow, {
    label: "Livraison"
  }, "Colis neutre, sous 3 \xE0 5 jours"), /*#__PURE__*/React.createElement(DetailRow, {
    label: "Retours"
  }, "14 jours, sans question"), /*#__PURE__*/React.createElement(DetailRow, {
    label: "Discr\xE9tion"
  }, "Libell\xE9 bancaire anonyme"))))));
}
function DetailRow({
  label,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 14,
      alignItems: 'baseline'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 700,
      fontSize: 11,
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: 'var(--color-accent-dark)',
      minWidth: 90
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 13.5,
      color: 'var(--color-text-secondary)'
    }
  }, children));
}
Object.assign(window, {
  CategoryPage,
  ProductPage,
  DetailRow
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/boutique/screens-catalog.jsx", error: String((e && e.message) || e) }); }

// ui_kits/boutique/screens-home.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
// Écrans — Le Cabinet d'Iris
const DS_screens = window.LeCabinetDIrisDesignSystem_55ae4c;

// ── Homepage ──────────────────────────────────────────────
function HomePage({
  go
}) {
  const {
    Button,
    SectionTitle,
    IrisQuote,
    ProductCard,
    CategoryTile,
    Separator
  } = DS_screens;
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("section", {
    style: {
      position: 'relative',
      height: 440,
      background: 'var(--color-primary-dark)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 40
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: '3.5rem',
      fontWeight: 400,
      color: 'var(--color-text-on-dark)',
      letterSpacing: '0.1em',
      margin: '0 0 10px'
    }
  }, "Le Cabinet d'Iris"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: '1.1rem',
      color: 'var(--color-accent)',
      letterSpacing: '0.2em',
      textTransform: 'uppercase',
      margin: '0 0 40px'
    }
  }, "Collection priv\xE9e de curiosit\xE9s sensuelles"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: () => go('category', {
      category: 'Les Étoffes'
    })
  }, "Entrer dans la Vitrine")), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      bottom: 14,
      right: 18,
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 10,
      letterSpacing: '0.1em',
      color: 'var(--color-text-on-dark)',
      opacity: 0.35
    }
  }, "Photo clair-obscur \xE0 fournir")), /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '60px 40px 50px'
    }
  }, /*#__PURE__*/React.createElement(SectionTitle, {
    subtitle: "Quatre pi\xE8ces choisies"
  }, "S\xE9lection d'Iris"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 18,
      marginTop: 36
    }
  }, HOME_SELECTION.map(p => /*#__PURE__*/React.createElement(ProductCard, _extends({
    key: p.name
  }, p, {
    onClick: () => go('product', {
      product: p,
      category: p.category
    })
  }))))), /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '10px 40px 60px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 18
    }
  }, /*#__PURE__*/React.createElement(CategoryTile, {
    name: "La Vitrine",
    height: 260,
    description: "Lingerie fine, nuits de soie et \xE9lixirs d'alc\xF4ve \u2014 l'\xE9tage que l'on visite en plein jour.",
    onClick: () => go('category', {
      category: 'Les Étoffes'
    })
  }), /*#__PURE__*/React.createElement(CategoryTile, {
    name: "Le Cabinet",
    tone: "cabinet",
    height: 260,
    description: "Iris a rassembl\xE9 ici ce qu'elle ne montre qu'\xE0 ceux qui poussent la porte.",
    onClick: () => go('gate')
  }))), /*#__PURE__*/React.createElement("section", {
    style: {
      background: 'var(--color-primary)',
      padding: '26px 0'
    }
  }, /*#__PURE__*/React.createElement(IrisQuote, null, "Le d\xE9sir est une curiosit\xE9 qui se collectionne.")), /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '56px 40px 70px'
    }
  }, /*#__PURE__*/React.createElement(SectionTitle, {
    subtitle: "Le journal de la maison"
  }, "Les Carnets d'Iris"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 18,
      marginTop: 36
    }
  }, CARNETS.map(c => /*#__PURE__*/React.createElement(CarnetCard, _extends({
    key: c.title
  }, c))))));
}
function CarnetCard({
  title,
  date
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      border: `0.5px solid ${hover ? 'var(--color-accent)' : 'var(--color-border)'}`,
      transition: 'border-color 0.3s ease',
      padding: '26px 24px 24px',
      cursor: 'pointer',
      background: 'var(--color-background)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--color-accent)',
      display: 'block',
      marginBottom: 12
    }
  }, /*#__PURE__*/React.createElement(IconFeather, {
    size: 22
  })), /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 600,
      fontSize: 19,
      color: 'var(--color-primary)',
      margin: '0 0 8px',
      letterSpacing: '0.02em'
    }
  }, title), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 11.5,
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: 'var(--color-text-secondary)'
    }
  }, date));
}

// ── Sas du Cabinet ────────────────────────────────────────
function GatePage({
  go
}) {
  const {
    Button
  } = DS_screens;
  return /*#__PURE__*/React.createElement("section", {
    style: {
      minHeight: 560,
      background: 'var(--color-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 40
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 64,
      height: 82,
      margin: '0 auto 28px',
      border: '1px solid var(--color-accent)',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'var(--font-serif-display)',
      fontSize: 38,
      color: 'var(--color-accent)',
      opacity: 0.85
    }
  }, "I"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontSize: '2.5rem',
      fontWeight: 400,
      color: 'var(--color-text-on-dark)',
      letterSpacing: '0.15em',
      margin: '0 0 15px'
    }
  }, "Le Cabinet"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      color: 'var(--color-text-on-dark)',
      opacity: 0.7,
      maxWidth: 500,
      margin: '0 auto 10px',
      lineHeight: 1.7
    }
  }, "Iris a rassembl\xE9 ici ce qu'elle ne montre qu'\xE0 ceux qui poussent la porte."), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontSize: 13,
      color: 'var(--color-text-on-dark)',
      opacity: 0.7,
      margin: '0 auto 30px'
    }
  }, "En entrant, vous confirmez avoir plus de 18 ans."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 22
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    onClick: () => go('cabinet')
  }, "Entrer"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    onClick: () => go('home')
  }, "Retourner \xE0 la Vitrine"))));
}

// ── Le Cabinet (univers niveau 2) ─────────────────────────
function CabinetPage({
  go
}) {
  const {
    CategoryTile,
    IrisQuote
  } = DS_screens;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--color-primary)'
    }
  }, /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 1100,
      margin: '0 auto',
      padding: '54px 40px 60px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      marginBottom: 40
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-serif-display)',
      fontWeight: 400,
      fontSize: '2.2rem',
      letterSpacing: '0.15em',
      color: 'var(--color-text-on-dark)',
      margin: '0 0 8px'
    }
  }, "Le Cabinet"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: 'var(--font-sans-body)',
      fontWeight: 300,
      fontSize: 13,
      letterSpacing: '0.2em',
      textTransform: 'uppercase',
      color: 'var(--color-accent)',
      margin: 0
    }
  }, "Six pi\xE8ces, six curiosit\xE9s")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 18
    }
  }, CABINET_CATEGORIES.map(c => /*#__PURE__*/React.createElement(CategoryTile, {
    key: c.name,
    name: c.name,
    description: c.desc,
    tone: "cabinet",
    height: 190,
    onClick: () => CATALOG[c.name] ? go('category', {
      category: c.name
    }) : null
  })))), /*#__PURE__*/React.createElement(IrisQuote, null, "On ne force jamais une porte. On la pousse."), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 40
    }
  }));
}
Object.assign(window, {
  HomePage,
  GatePage,
  CabinetPage,
  CarnetCard
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/boutique/screens-home.jsx", error: String((e && e.message) || e) }); }

__ds_ns.CategoryTile = __ds_scope.CategoryTile;

__ds_ns.ProductCard = __ds_scope.ProductCard;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.EditorialText = __ds_scope.EditorialText;

__ds_ns.IrisQuote = __ds_scope.IrisQuote;

__ds_ns.PriceTag = __ds_scope.PriceTag;

__ds_ns.ReassuranceItem = __ds_scope.ReassuranceItem;

__ds_ns.SectionTitle = __ds_scope.SectionTitle;

__ds_ns.Separator = __ds_scope.Separator;

})();

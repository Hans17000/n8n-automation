Bouton de marque : serif uppercase espacé, transitions 0.3s ease, jamais d'ombre ni de radius (sauf cabinet-entry, 2px).

```jsx
<Button variant="primary">Ajouter au panier</Button>
<Button variant="secondary" href="/la-vitrine">Entrer dans la Vitrine</Button>
<Button variant="cabinet-entry" href="/le-cabinet">Poussez la porte</Button>
<Button variant="ghost">Retourner à la Vitrine</Button>
```

- `primary` : fond or antique, texte noir d'encre — CTA principal (ajout panier, « Entrer »).
- `secondary` : outline or, se remplit d'or au hover — CTA hero sur fond sombre.
- `cabinet-entry` : Cormorant italique, pas d'uppercase — réservé au lien « Poussez la porte ».
- `ghost` : lien Lato souligné, opacité 0.5 — actions de retrait sur fond sombre.

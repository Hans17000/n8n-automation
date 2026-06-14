Bloc de réassurance, disposé en 4 colonnes sur fond noir d'encre.

```jsx
<div style={{ background: 'var(--color-primary)', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
  <ReassuranceItem icon={<PackageIcon />} label="Livraison discrète" />
  <ReassuranceItem icon={<LockIcon />} label="Paiement sécurisé" />
  <ReassuranceItem icon={<KeyIcon />} label="Curation Iris" />
  <ReassuranceItem icon={<UndoIcon />} label="Retours sous 14j" />
</div>
```

L'icône hérite `currentColor` (or antique). Libellés canoniques : « Livraison discrète », « Paiement sécurisé », « Curation Iris », « Retours sous 14j ».

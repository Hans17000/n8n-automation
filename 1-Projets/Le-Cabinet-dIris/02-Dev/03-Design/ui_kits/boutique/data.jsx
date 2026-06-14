// Données de démonstration — Le Cabinet d'Iris
const CATALOG = {
  'Les Étoffes': {
    tone: 'vitrine',
    intro: 'La dentelle est une écriture. Iris a réuni ici les étoffes qui se lisent du bout des doigts — guipures, tulles et soies qui promettent sans jamais tout dire.',
    products: [
      { name: 'Soutien-gorge Aurore', price: 89 },
      { name: 'Culotte Héloïse', price: 45 },
      { name: 'Body Insomnie', price: 125, badge: 'rare' },
      { name: 'Guêpière Comtesse', price: 160 },
      { name: 'Porte-jarretelles Minuit', price: 65 },
      { name: 'Caraco Aube Pâle', price: 78 },
    ],
  },
  'Les Nuits': {
    tone: 'vitrine',
    intro: 'Ce que l\u2019on porte quand on ne porte presque rien. Nuisettes et kimonos pour les heures où la maison se tait.',
    products: [
      { name: 'Nuisette Minuit', price: 145, badge: 'rare' },
      { name: 'Kimono Songe', price: 190 },
      { name: 'Nuisette Velours d\u2019Ombre', price: 130 },
      { name: 'Pyjama Confidence', price: 110 },
    ],
  },
  'Les Voiles': {
    tone: 'vitrine',
    intro: 'Des transparences qui voilent mieux qu\u2019elles ne dévoilent.',
    products: [
      { name: 'Peignoir Brume', price: 95 },
      { name: 'Robe d\u2019intérieur Solstice', price: 175 },
      { name: 'Voile Équivoque', price: 85 },
    ],
  },
  'Les Élixirs': {
    tone: 'vitrine',
    intro: 'Huiles, baumes et parfums d\u2019alcôve — la chimie discrète des soirs choisis.',
    products: [
      { name: 'Huile Lueur', price: 38 },
      { name: 'Baume Avant-Nuit', price: 29 },
      { name: 'Brume d\u2019Oreiller №3', price: 42, badge: 'rare' },
      { name: 'Bougie de Massage Cire Douce', price: 35 },
    ],
  },
  'Les Écrins': {
    tone: 'vitrine',
    intro: 'Coffrets composés par Iris — pour offrir sans expliquer.',
    products: [
      { name: 'Écrin Première Fois', price: 120 },
      { name: 'Écrin Anniversaire', price: 180 },
      { name: 'Écrin Carte Blanche', price: 250, badge: 'rare' },
    ],
  },
  'Les Apparitions': {
    tone: 'cabinet',
    intro: 'Tenues qui n\u2019existent que le temps d\u2019une apparition.',
    products: [
      { name: 'Harnais Dentelle Noire', price: 95, badge: 'cabinet' },
      { name: 'Cape Équinoxe', price: 210, badge: 'cabinet' },
      { name: 'Masque Vénitien Or Mat', price: 75, badge: 'cabinet' },
    ],
  },
  'Le Boudoir Noir': {
    tone: 'cabinet',
    intro: 'Le velours a ses raisons. Pièces choisies pour qui sait demander.',
    products: [
      { name: 'Cravache Velours', price: 120, badge: 'cabinet' },
      { name: 'Menottes Soie & Laiton', price: 85, badge: 'cabinet' },
      { name: 'Flogger Cuir Patiné', price: 140, badge: 'rare' },
      { name: 'Bandeau Nuit Close', price: 48, badge: 'cabinet' },
    ],
  },
};

const CABINET_CATEGORIES = [
  { name: 'Les Apparitions', desc: 'Tenues qui n\u2019existent que le temps d\u2019une apparition.' },
  { name: 'Les Objets', desc: 'Curiosités de design, à poser ou à cacher.' },
  { name: 'Les Confessions', desc: 'Ce qui se murmure entre initiés.' },
  { name: 'Les Complicités', desc: 'À deux, ou davantage.' },
  { name: 'Le Boudoir Noir', desc: 'Le velours a ses raisons.' },
  { name: 'Les Caprices', desc: 'Les envies qui ne s\u2019expliquent pas.' },
];

const HOME_SELECTION = [
  { name: 'Body Insomnie', price: 125, category: 'Les Étoffes', badge: 'rare' },
  { name: 'Nuisette Minuit', price: 145, category: 'Les Nuits' },
  { name: 'Brume d\u2019Oreiller №3', price: 42, category: 'Les Élixirs' },
  { name: 'Écrin Carte Blanche', price: 250, category: 'Les Écrins', badge: 'rare' },
];

const CARNETS = [
  { title: 'L\u2019art de recevoir sans rien montrer', date: '12 mai 2026' },
  { title: 'Petite grammaire de la dentelle', date: '28 avril 2026' },
  { title: 'Du bon usage des clés anciennes', date: '9 avril 2026' },
];

Object.assign(window, { CATALOG, CABINET_CATEGORIES, HOME_SELECTION, CARNETS });

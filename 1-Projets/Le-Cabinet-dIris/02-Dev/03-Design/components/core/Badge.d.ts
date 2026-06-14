/**
 * Badge produit — « Pièce rare » (stock bas) ou « Cabinet » (catégorie niveau 2).
 */
export interface BadgeProps {
  /** 'rare' bordeaux bord doré · 'cabinet' prune */
  variant?: 'rare' | 'cabinet';
  /** Libellé ; par défaut « Pièce rare » / « Cabinet » */
  children?: React.ReactNode;
}
export declare function Badge(props: BadgeProps): JSX.Element;

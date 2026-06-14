/**
 * Prix doré Lato Light — format français (virgule, € après).
 */
export interface PriceTagProps {
  /** Nombre (89 → « 89,00 € ») ou chaîne déjà formatée */
  amount: number | string;
  /** 'sm' 14px grille dense · 'md' 16px grille · 'lg' 1.6rem fiche produit */
  size?: 'sm' | 'md' | 'lg';
  currency?: string;
}
export declare function PriceTag(props: PriceTagProps): JSX.Element;

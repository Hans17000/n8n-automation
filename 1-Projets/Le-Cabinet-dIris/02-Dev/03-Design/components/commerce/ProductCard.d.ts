/**
 * Miniature produit pour grilles catalogue.
 * @startingPoint section="Composants" subtitle="Miniature produit — hairline dorée, badge, prix doré" viewport="700x420"
 */
export interface ProductCardProps {
  name: string;
  /** Nombre (formaté « 89,00 € ») ou chaîne */
  price: number | string;
  /** URL image 3:4 ; placeholder monogramme si absent */
  image?: string;
  /** 'rare' ou 'cabinet' — coin haut-gauche */
  badge?: 'rare' | 'cabinet';
  /** Nom de catégorie, petit uppercase au-dessus du nom */
  category?: string;
  onClick?: () => void;
}
export declare function ProductCard(props: ProductCardProps): JSX.Element;

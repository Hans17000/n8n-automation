/**
 * Tuile catégorie / univers — fond noir d'encre (Vitrine) ou prune (Cabinet).
 */
export interface CategoryTileProps {
  /** Nom poétique : « Les Étoffes », « Le Boudoir Noir »… */
  name: string;
  /** Une ligne dans le ton d'Iris, italique or clair */
  description?: string;
  /** 'vitrine' fond encre · 'cabinet' fond prune */
  tone?: 'vitrine' | 'cabinet';
  onClick?: () => void;
  /** Hauteur px, 220 par défaut */
  height?: number;
}
export declare function CategoryTile(props: CategoryTileProps): JSX.Element;

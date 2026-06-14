/**
 * Bouton Le Cabinet d'Iris — or antique sur noir d'encre.
 * @startingPoint section="Composants" subtitle="Boutons primary, outline, « Poussez la porte », ghost" viewport="700x260"
 */
export interface ButtonProps {
  /** 'primary' fond or · 'secondary' outline or · 'cabinet-entry' italique nav · 'ghost' lien discret sur fond sombre */
  variant?: 'primary' | 'secondary' | 'cabinet-entry' | 'ghost';
  children?: React.ReactNode;
  /** Rend un <a> au lieu d'un <button> */
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  style?: React.CSSProperties;
}
export declare function Button(props: ButtonProps): JSX.Element;

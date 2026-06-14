/**
 * Titre de section centré, filets dorés latéraux, sous-titre uppercase doré optionnel.
 */
export interface SectionTitleProps {
  children: React.ReactNode;
  /** Sous-titre Lato 300 uppercase 0.2em doré */
  subtitle?: string;
  /** Texte ivoire pour fonds noir d'encre / prune */
  onDark?: boolean;
}
export declare function SectionTitle(props: SectionTitleProps): JSX.Element;

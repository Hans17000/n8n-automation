/**
 * Filet doré horizontal avec motif central discret.
 */
export interface SeparatorProps {
  /** Caractère central : 'I' (monogramme) ou '❦' (fleuron) */
  motif?: string;
  onDark?: boolean;
  style?: React.CSSProperties;
}
export declare function Separator(props: SeparatorProps): JSX.Element;

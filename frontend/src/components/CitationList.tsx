import type { Citation } from "../api/types";

type Props = {
  citations: Citation[];
};

export function CitationList({ citations }: Props) {
  if (citations.length === 0) return null;
  return (
    <div className="citations">
      <h3>引用来源</h3>
      {citations.map((citation) => (
        <details key={citation.chunk_id}>
          <summary>
            {citation.paper_title} · p.{citation.page_start}
            {citation.page_end !== citation.page_start ? `-${citation.page_end}` : ""} ·{" "}
            {citation.section}
          </summary>
          <blockquote>{citation.quote}</blockquote>
        </details>
      ))}
    </div>
  );
}

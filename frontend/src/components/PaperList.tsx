import type { Paper } from "../api/types";

type Props = {
  papers: Paper[];
  selectedId?: string;
  onSelect: (paper: Paper) => void;
};

export function PaperList({ papers, selectedId, onSelect }: Props) {
  if (papers.length === 0) {
    return <div className="empty">还没有论文，先上传一篇 PDF。</div>;
  }
  return (
    <div className="paper-list">
      {papers.map((paper) => (
        <button
          className={paper.id === selectedId ? "paper-row selected" : "paper-row"}
          key={paper.id}
          onClick={() => onSelect(paper)}
        >
          <span>
            <strong>{paper.title || paper.file_name}</strong>
            <small>{paper.authors?.join(", ") || paper.file_name}</small>
          </span>
          <em className={`status ${paper.status}`}>{paper.status}</em>
        </button>
      ))}
    </div>
  );
}

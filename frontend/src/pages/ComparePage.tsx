import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { comparePapers, summarizePaper } from "../api/summaries";
import type { Paper } from "../api/types";

type Props = {
  papers: Paper[];
};

export function ComparePage({ papers }: Props) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [paperId, setPaperId] = useState("");
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function runSummary() {
    if (!paperId) return;
    setBusy(true);
    setError("");
    try {
      const result = await summarizePaper(paperId);
      setOutput(result.summary);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "总结失败");
    } finally {
      setBusy(false);
    }
  }

  async function runCompare() {
    setBusy(true);
    setError("");
    try {
      const result = await comparePapers(selectedIds);
      setOutput(result.comparison);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "对比失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-grid">
      <section className="panel">
        <h2>总结与对比</h2>
        <label className="field">
          <span>单篇总结</span>
          <select value={paperId} onChange={(event) => setPaperId(event.target.value)}>
            <option value="">选择论文</option>
            {papers.map((paper) => (
              <option key={paper.id} value={paper.id}>
                {paper.title}
              </option>
            ))}
          </select>
        </label>
        <button className="primary" onClick={() => void runSummary()} disabled={busy || !paperId}>
          生成总结
        </button>
        <div className="divider" />
        <h3>多论文对比</h3>
        <div className="check-list">
          {papers.map((paper) => (
            <label key={paper.id}>
              <input
                type="checkbox"
                checked={selectedIds.includes(paper.id)}
                onChange={(event) => {
                  setSelectedIds((ids) =>
                    event.target.checked ? [...ids, paper.id] : ids.filter((id) => id !== paper.id)
                  );
                }}
              />
              <span>{paper.title}</span>
            </label>
          ))}
        </div>
        <button
          className="primary"
          onClick={() => void runCompare()}
          disabled={busy || selectedIds.length < 2}
        >
          生成对比表
        </button>
        {error ? <p className="error">{error}</p> : null}
      </section>
      <section className="panel markdown-panel">
        {output ? <ReactMarkdown>{output}</ReactMarkdown> : <div className="empty">结果将在这里显示。</div>}
      </section>
    </div>
  );
}

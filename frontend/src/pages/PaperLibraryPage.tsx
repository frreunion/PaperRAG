import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getPaper, listPapers, uploadPaper } from "../api/papers";
import type { Paper } from "../api/types";
import { PaperList } from "../components/PaperList";
import { UploadPanel } from "../components/UploadPanel";

type Props = {
  selectedPaper: Paper | null;
  onSelectPaper: (paper: Paper) => void;
};

export function PaperLibraryPage({ selectedPaper, onSelectPaper }: Props) {
  const queryClient = useQueryClient();
  const papersQuery = useQuery({ queryKey: ["papers"], queryFn: listPapers });
  const uploadMutation = useMutation({
    mutationFn: uploadPaper,
    onSuccess: async (paper) => {
      await queryClient.invalidateQueries({ queryKey: ["papers"] });
      onSelectPaper(paper);
    }
  });
  const detailQuery = useQuery({
    queryKey: ["paper", selectedPaper?.id],
    queryFn: () => getPaper(selectedPaper!.id),
    enabled: Boolean(selectedPaper?.id)
  });
  const paper = detailQuery.data ?? selectedPaper;

  return (
    <div className="page-grid">
      <div className="stack">
        <UploadPanel onUpload={(file) => uploadMutation.mutateAsync(file).then(() => undefined)} />
        <section className="panel">
          <h2>论文列表</h2>
          {papersQuery.isLoading ? (
            <div className="empty">正在加载论文...</div>
          ) : (
            <PaperList
              papers={papersQuery.data ?? []}
              selectedId={paper?.id}
              onSelect={onSelectPaper}
            />
          )}
        </section>
      </div>
      <section className="panel detail-panel">
        <h2>论文详情</h2>
        {paper ? (
          <div className="detail">
            <div className={`status ${paper.status}`}>{paper.status}</div>
            <h3>{paper.title}</h3>
            <p>{paper.authors?.join(", ") || "作者未识别"}</p>
            <p>{paper.abstract || "暂无摘要。"}</p>
            {paper.error_message ? <p className="error">{paper.error_message}</p> : null}
          </div>
        ) : (
          <div className="empty">选择一篇论文查看详情。</div>
        )}
      </section>
    </div>
  );
}

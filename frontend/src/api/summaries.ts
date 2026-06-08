import { apiRequest } from "./client";
import type { Citation } from "./types";

export function summarizePaper(paperId: string) {
  return apiRequest<{ paper_id: string; summary: string; citations: Citation[] }>(
    `/api/summaries/paper/${paperId}`,
    { method: "POST" }
  );
}

export function comparePapers(paperIds: string[]) {
  return apiRequest<{ comparison: string; citations: Citation[] }>("/api/summaries/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_ids: paperIds })
  });
}

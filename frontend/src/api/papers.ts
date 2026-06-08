import { apiRequest } from "./client";
import type { Paper } from "./types";

export function listPapers() {
  return apiRequest<Paper[]>("/api/papers");
}

export function getPaper(id: string) {
  return apiRequest<Paper>(`/api/papers/${id}`);
}

export function uploadPaper(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<Paper>("/api/papers", {
    method: "POST",
    body: formData
  });
}

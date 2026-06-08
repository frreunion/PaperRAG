import { apiRequest } from "./client";
import type { Answer } from "./types";

export type Chat = {
  id: string;
  title: string;
  scope: { paper_ids: string[] };
};

export function createChat(paperIds: string[]) {
  return apiRequest<Chat>("/api/chats", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_ids: paperIds, title: "Paper discussion" })
  });
}

export function askQuestion(sessionId: string, question: string) {
  return apiRequest<Answer>(`/api/chats/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
}

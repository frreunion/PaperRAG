import { Send } from "lucide-react";
import { useState } from "react";
import { askQuestion, createChat } from "../api/chats";
import type { Answer, Paper } from "../api/types";
import { CitationList } from "../components/CitationList";

type Props = {
  papers: Paper[];
};

type Message = { role: "user" | "assistant"; content: string; answer?: Answer };

export function ChatPage({ papers }: Props) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    const currentQuestion = question;
    setQuestion("");
    setMessages((items) => [...items, { role: "user", content: currentQuestion }]);
    try {
      const chat = sessionId ? { id: sessionId } : await createChat(selectedIds);
      if (!sessionId) setSessionId(chat.id);
      const answer = await askQuestion(chat.id, currentQuestion);
      setMessages((items) => [
        ...items,
        { role: "assistant", content: answer.answer, answer }
      ]);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "问答失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat-layout">
      <section className="panel">
        <h2>检索范围</h2>
        <div className="check-list">
          {papers.map((paper) => (
            <label key={paper.id}>
              <input
                type="checkbox"
                checked={selectedIds.includes(paper.id)}
                onChange={(event) => {
                  setSessionId("");
                  setSelectedIds((ids) =>
                    event.target.checked ? [...ids, paper.id] : ids.filter((id) => id !== paper.id)
                  );
                }}
              />
              <span>{paper.title}</span>
            </label>
          ))}
        </div>
      </section>
      <section className="panel chat-panel">
        <h2>论文问答</h2>
        <div className="messages">
          {messages.length === 0 ? <div className="empty">选择论文后开始提问。</div> : null}
          {messages.map((message, index) => (
            <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <p>{message.content}</p>
              {message.answer ? <CitationList citations={message.answer.citations} /> : null}
            </div>
          ))}
        </div>
        <div className="composer">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如：这篇论文的核心创新是什么？"
            onKeyDown={(event) => {
              if (event.key === "Enter") void submit();
            }}
          />
          <button onClick={() => void submit()} disabled={busy} title="发送问题">
            <Send size={18} />
          </button>
        </div>
        {error ? <p className="error">{error}</p> : null}
      </section>
    </div>
  );
}

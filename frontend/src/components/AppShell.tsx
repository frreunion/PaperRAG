import { BookOpen, GitCompare, MessageSquareText } from "lucide-react";

type View = "library" | "chat" | "compare";

type Props = {
  view: View;
  onViewChange: (view: View) => void;
  children: React.ReactNode;
};

export function AppShell({ view, onViewChange, children }: Props) {
  const items = [
    { id: "library" as const, label: "论文库", icon: BookOpen },
    { id: "chat" as const, label: "论文问答", icon: MessageSquareText },
    { id: "compare" as const, label: "多论文对比", icon: GitCompare }
  ];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div>
            <h1>论文 RAG 助手</h1>
            <p>科研阅读工作台</p>
          </div>
        </div>
        <nav>
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={view === item.id ? "nav-item active" : "nav-item"}
                onClick={() => onViewChange(item.id)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

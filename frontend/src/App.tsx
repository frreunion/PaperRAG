import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { listPapers } from "./api/papers";
import type { Paper } from "./api/types";
import { AppShell } from "./components/AppShell";
import { ChatPage } from "./pages/ChatPage";
import { ComparePage } from "./pages/ComparePage";
import { PaperLibraryPage } from "./pages/PaperLibraryPage";

type View = "library" | "chat" | "compare";

export function App() {
  const [view, setView] = useState<View>("library");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const papersQuery = useQuery({ queryKey: ["papers"], queryFn: listPapers });
  const papers = papersQuery.data ?? [];

  return (
    <AppShell view={view} onViewChange={setView}>
      {view === "library" ? (
        <PaperLibraryPage selectedPaper={selectedPaper} onSelectPaper={setSelectedPaper} />
      ) : null}
      {view === "chat" ? <ChatPage papers={papers} /> : null}
      {view === "compare" ? <ComparePage papers={papers} /> : null}
    </AppShell>
  );
}

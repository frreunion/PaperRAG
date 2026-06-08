export type Paper = {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  year: number | null;
  venue: string;
  file_name: string;
  status: "uploaded" | "parsing" | "indexed" | "failed";
  error_message: string;
};

export type Citation = {
  paper_id: string;
  paper_title: string;
  chunk_id: string;
  page_start: number;
  page_end: number;
  section: string;
  quote: string;
};

export type Answer = {
  answer: string;
  citations: Citation[];
};

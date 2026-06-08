export type Note = {
  id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
};

export type NoteDraft = {
  id?: string;
  title: string;
  content: string;
  tags: string[];
};

export type SearchResult = {
  noteId: string;
  noteTitle: string;
  chunkText: string;
  similarityScore: number;
};

export type ChatResponse = {
  answer: string;
  sources: SearchResult[];
};

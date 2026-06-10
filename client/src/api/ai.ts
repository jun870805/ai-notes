import { apiClient } from "./client";
import type { ChatResponse, SearchResult } from "../types";

type SearchResultApi = {
  note_id: string;
  note_title: string;
  chunk_text: string;
  similarity_score: number;
};

type SearchResponseApi = {
  results: SearchResultApi[];
};

type ChatResponseApi = {
  answer: string;
  sources: SearchResultApi[];
};

function mapSearchResult(result: SearchResultApi): SearchResult {
  return {
    noteId: result.note_id,
    noteTitle: result.note_title,
    chunkText: result.chunk_text,
    similarityScore: result.similarity_score,
  };
}

export async function searchNotes(query: string, topK = 5) {
  const response = await apiClient.post<SearchResponseApi>("/ai/search", { query, top_k: topK });
  return response.results.map(mapSearchResult);
}

export async function chatWithNotes(question: string, topK = 3): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponseApi>("/ai/chat", { question, top_k: topK });
  return {
    answer: response.answer,
    sources: response.sources.map(mapSearchResult),
  };
}

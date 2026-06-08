import { describe, expect, it } from "vitest";
import { buildChatAnswer, buildSearchResults, initialNotes } from "./mockData";

describe("mockData utilities", () => {
  it("returns ranked search results capped at five items", () => {
    const results = buildSearchResults(initialNotes, "FastAPI token 驗證");

    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5);
    expect(results[0]?.noteTitle).toContain("FastAPI");
    expect(results[0]?.similarityScore).toBeGreaterThan(0.55);
  });

  it("returns an empty array when query terms do not match current notes", () => {
    const results = buildSearchResults(initialNotes, "kubernetes ingress controller");

    expect(results).toEqual([]);
  });

  it("builds a citation-based answer when sources exist", () => {
    const sources = buildSearchResults(initialNotes, "pgvector 語意搜尋");
    const response = buildChatAnswer("pgvector 怎麼接語意搜尋？", sources);

    expect(response.answer).toContain("根據");
    expect(response.answer).toContain("pgvector");
    expect(response.sources).toEqual(sources);
  });

  it("returns an insufficient-data answer when no sources exist", () => {
    const response = buildChatAnswer("沒有資料的問題", []);

    expect(response.sources).toEqual([]);
    expect(response.answer).toContain("目前筆記資料不足");
  });
});

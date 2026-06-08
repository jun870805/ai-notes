import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { renderApp } from "./test/utils";

describe("client app", () => {
  it("renders localized primary navigation and product title", () => {
    renderApp("/notes");

    expect(screen.getByRole("heading", { name: "AI 工程筆記" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "筆記" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "AI 搜尋" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "AI 對話" })).toBeInTheDocument();
  });

  it("shows a consistent three-section layout for AI 搜尋", () => {
    renderApp("/search");

    expect(screen.getByRole("heading", { name: "AI 搜尋" })).toBeInTheDocument();
    expect(screen.getByLabelText("搜尋問題")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "搜尋結果" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "來源" })).toBeInTheDocument();
  });

  it("shows a consistent three-section layout for AI 對話", () => {
    renderApp("/chat");

    expect(screen.getByRole("heading", { name: "AI 對話" })).toBeInTheDocument();
    expect(screen.getByLabelText("問題")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "回答" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "來源" })).toBeInTheDocument();
  });

  it("saves a new note and opens the editor for that note", async () => {
    const user = userEvent.setup();
    renderApp("/notes/new");

    await user.clear(screen.getByLabelText("標題"));
    await user.type(screen.getByLabelText("標題"), "新的測試筆記");
    await user.clear(screen.getByLabelText("Markdown 內容"));
    await user.type(screen.getByLabelText("Markdown 內容"), "# 測試內容");
    await user.click(screen.getByRole("button", { name: "儲存筆記" }));

    expect(screen.getByRole("heading", { name: "編輯筆記" })).toBeInTheDocument();
    expect(screen.getByDisplayValue("新的測試筆記")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "刪除筆記" })).toBeInTheDocument();
  });

  it("navigates between tabs without losing the active tab label", async () => {
    const user = userEvent.setup();
    renderApp("/notes");

    await user.click(screen.getByRole("link", { name: "AI 搜尋" }));
    expect(screen.getByRole("heading", { name: "AI 搜尋" })).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "AI 對話" }));
    expect(screen.getByRole("heading", { name: "AI 對話" })).toBeInTheDocument();
  });
});

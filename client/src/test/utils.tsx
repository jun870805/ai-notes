import type { PropsWithChildren } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

export function renderApp(initialPath = "/notes") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <App />
    </MemoryRouter>,
  );
}

export function TestWrapper({ children, initialPath = "/notes" }: PropsWithChildren<{ initialPath?: string }>) {
  return <MemoryRouter initialEntries={[initialPath]}>{children}</MemoryRouter>;
}

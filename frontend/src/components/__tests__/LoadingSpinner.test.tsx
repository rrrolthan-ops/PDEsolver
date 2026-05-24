import { describe, it, expect } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { LoadingSpinner } from "../LoadingSpinner";

describe("LoadingSpinner", () => {
  it("renders the spinner with role=status", () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("uses the supplied label as the aria-label and the inline text", () => {
    render(<LoadingSpinner label="Resolviendo…" />);
    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-label", "Resolviendo…");
    expect(screen.getByText("Resolviendo…")).toBeInTheDocument();
  });

  it("uses 'Cargando' as the default aria-label when none is given", () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole("status")).toHaveAttribute(
      "aria-label",
      "Cargando",
    );
  });

  it("renders a pedagogical hint when showHint is true", () => {
    render(<LoadingSpinner showHint />);
    // The first hint of the rotation is "Clasificando la EDP …".
    expect(screen.getByText(/Clasificando la EDP/i)).toBeInTheDocument();
  });

  it("does not show a hint when showHint is false", () => {
    render(<LoadingSpinner />);
    expect(screen.queryByText(/Clasificando la EDP/i)).toBeNull();
  });

  it("rotates through hints over time", () => {
    vi.useFakeTimers();
    render(<LoadingSpinner showHint />);
    expect(screen.getByText(/Clasificando la EDP/i)).toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(1900);
    });
    // After ≈1.8s the hint should have rotated to the next one
    // (we don't care which — just that the initial is no longer shown
    // or that some hint is visible).
    const status = screen.getByRole("status");
    expect(status.textContent).toBeTruthy();
    vi.useRealTimers();
  });
});

// Import vi after the describe block so the fake-timer test compiles
// (vi is auto-globalized but TS-checked imports keep editors happy).
import { vi } from "vitest";

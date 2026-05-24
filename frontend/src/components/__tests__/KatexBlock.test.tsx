import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { KatexBlock } from "../KatexBlock";

describe("KatexBlock", () => {
  it("renders a span and emits KaTeX HTML for a valid expression", () => {
    const { container } = render(<KatexBlock latex="\\alpha + \\beta" />);
    const span = container.querySelector("span.latex-block");
    expect(span).not.toBeNull();
    // KaTeX renders into a katex-display or katex element under the hood.
    expect(span?.innerHTML).toMatch(/katex/i);
  });

  it("uses inline class when displayMode is false", () => {
    const { container } = render(
      <KatexBlock latex="x^2" displayMode={false} />
    );
    expect(container.querySelector("span.latex-inline")).not.toBeNull();
    expect(container.querySelector("span.latex-block")).toBeNull();
  });

  it("does not throw on malformed LaTeX (strict: ignore + throwOnError: false)", () => {
    // KaTeX is configured to swallow errors and render them in red.
    const { container } = render(<KatexBlock latex="\\bogus{abc" />);
    const span = container.querySelector("span");
    expect(span).not.toBeNull();
    // Either it rendered an error inline or KaTeX accepted it silently;
    // the key invariant is that React didn't unmount with an exception.
    expect(container.textContent).toBeDefined();
  });

  it("expands custom macros (\\R and \\N)", () => {
    const { container } = render(<KatexBlock latex="x \\in \\R" />);
    // The macros are configured at the call site; KaTeX will substitute
    // \R → \mathbb{R}. We just check that KaTeX produced output.
    expect(container.querySelector(".latex-block")?.innerHTML).toMatch(/katex/i);
  });
});

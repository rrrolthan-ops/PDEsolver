import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DetailSlider, shouldShow } from "../DetailSlider";

describe("DetailSlider", () => {
  it("renders the current detail level label", () => {
    render(<DetailSlider value="basic" onChange={() => {}} />);
    expect(screen.getByText("Básico")).toBeInTheDocument();
  });

  it("renders the intermediate label", () => {
    render(<DetailSlider value="intermediate" onChange={() => {}} />);
    expect(screen.getByText("Intermedio")).toBeInTheDocument();
  });

  it("calls onChange with the right level when the slider moves", () => {
    const onChange = vi.fn();
    render(<DetailSlider value="basic" onChange={onChange} />);
    const range = screen.getByRole("slider") as HTMLInputElement;
    // Move to index 2 → "exhaustive".
    fireEvent.change(range, { target: { value: "2" } });
    expect(onChange).toHaveBeenCalledWith("exhaustive");
  });

  it("slider value reflects the current level index", () => {
    const { rerender } = render(
      <DetailSlider value="basic" onChange={() => {}} />
    );
    const range = screen.getByRole("slider") as HTMLInputElement;
    expect(range.value).toBe("0");

    rerender(<DetailSlider value="intermediate" onChange={() => {}} />);
    expect(range.value).toBe("1");

    rerender(<DetailSlider value="exhaustive" onChange={() => {}} />);
    expect(range.value).toBe("2");
  });
});

describe("shouldShow", () => {
  it("shows basic steps at every detail level", () => {
    expect(shouldShow("basic", "basic")).toBe(true);
    expect(shouldShow("basic", "intermediate")).toBe(true);
    expect(shouldShow("basic", "exhaustive")).toBe(true);
  });

  it("shows intermediate steps only at intermediate or above", () => {
    expect(shouldShow("intermediate", "basic")).toBe(false);
    expect(shouldShow("intermediate", "intermediate")).toBe(true);
    expect(shouldShow("intermediate", "exhaustive")).toBe(true);
  });

  it("shows exhaustive steps only at exhaustive", () => {
    expect(shouldShow("exhaustive", "basic")).toBe(false);
    expect(shouldShow("exhaustive", "intermediate")).toBe(false);
    expect(shouldShow("exhaustive", "exhaustive")).toBe(true);
  });
});

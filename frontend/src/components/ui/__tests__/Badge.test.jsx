import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Badge from "../Badge";

describe("Badge", () => {
  it("renders its children", () => {
    render(<Badge>Active</Badge>);

    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("uses the default variant when none is provided", () => {
    render(<Badge>Default</Badge>);

    expect(screen.getByText("Default")).toHaveClass(
      "bg-slate-100",
      "text-slate-700",
    );
  });

  it.each([
    ["success", "bg-emerald-100", "text-emerald-700"],
    ["warning", "bg-amber-100", "text-amber-700"],
    ["danger", "bg-red-100", "text-red-700"],
    ["info", "bg-blue-100", "text-blue-700"],
  ])("applies the %s variant", (variant, background, textColor) => {
    render(<Badge variant={variant}>Status</Badge>);

    expect(screen.getByText("Status")).toHaveClass(background, textColor);
  });

  it("renders its children when the value is not a string", () => {
    render(<Badge><span>Custom status</span></Badge>);

    expect(screen.getByText("Custom status")).toBeInTheDocument();
  });
});
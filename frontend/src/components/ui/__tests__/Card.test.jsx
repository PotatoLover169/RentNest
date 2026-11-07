import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Card from "../Card";

describe("Card", () => {
  it("renders its children", () => {
    render(<Card>Property details</Card>);

    expect(screen.getByText("Property details")).toBeInTheDocument();
  });

  it("renders as a section element", () => {
    const { container } = render(<Card>Content</Card>);

    expect(container.querySelector("section")).toBeInTheDocument();
  });

  it("applies its default styling", () => {
    render(<Card>Content</Card>);

    expect(screen.getByText("Content")).toHaveClass(
      "rounded-xl",
      "border",
      "bg-white",
      "shadow-sm",
    );
  });

  it("forwards custom class names", () => {
    render(<Card className="p-6">Content</Card>);

    expect(screen.getByText("Content")).toHaveClass("p-6");
  });

  it("supports nested content", () => {
    render(
      <Card>
        <h2>Property</h2>
        <p>Two-bedroom apartment</p>
      </Card>,
    );

    expect(screen.getByRole("heading", { name: "Property" }))
      .toBeInTheDocument();
    expect(screen.getByText("Two-bedroom apartment"))
      .toBeInTheDocument();
  });
});
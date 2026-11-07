import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import Button from "../Button";

describe("Button", () => {
  it("renders its children", () => {
    render(<Button>Save changes</Button>);

    expect(
      screen.getByRole("button", { name: "Save changes" }),
    ).toBeInTheDocument();
  });

  it("uses button type by default", () => {
    render(<Button>Click me</Button>);

    expect(screen.getByRole("button")).toHaveAttribute("type", "button");
  });

  it("supports a custom button type", () => {
    render(<Button type="submit">Submit</Button>);

    expect(screen.getByRole("button")).toHaveAttribute("type", "submit");
  });

  it.each([
    ["primary", "bg-slate-900"],
    ["secondary", "bg-white"],
    ["danger", "bg-red-600"],
    ["ghost", "text-slate-600"],
  ])("applies the %s variant", (variant, expectedClass) => {
    render(<Button variant={variant}>Action</Button>);

    expect(screen.getByRole("button")).toHaveClass(expectedClass);
  });

  it.each([
    ["sm", "px-3"],
    ["md", "px-4"],
    ["lg", "px-5"],
  ])("applies the %s size", (size, expectedClass) => {
    render(<Button size={size}>Action</Button>);

    expect(screen.getByRole("button")).toHaveClass(expectedClass);
  });

  it("supports the disabled state", () => {
    render(<Button disabled>Save</Button>);

    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("forwards custom class names", () => {
    render(<Button className="w-full">Save</Button>);

    expect(screen.getByRole("button")).toHaveClass("w-full");
  });

  it("forwards click handlers", () => {
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Save</Button>);
    fireEvent.click(screen.getByRole("button"));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("forwards additional button attributes", () => {
    render(<Button aria-label="Save record">Save</Button>);

    expect(screen.getByRole("button", { name: "Save record" }))
      .toBeInTheDocument();
  });
});
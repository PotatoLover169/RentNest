import { describe, expect, it } from "vitest";
import * as UI from "../index";

describe("UI component exports", () => {
  it("exports the reusable UI components", () => {
    expect(UI.Badge).toBeTypeOf("function");
    expect(UI.Button).toBeTypeOf("function");
    expect(UI.Card).toBeTypeOf("function");
    expect(UI.EmptyState).toBeTypeOf("function");
    expect(UI.ErrorState).toBeTypeOf("function");
    expect(UI.LoadingState).toBeTypeOf("function");
    expect(UI.PageHeader).toBeTypeOf("function");
  });
});
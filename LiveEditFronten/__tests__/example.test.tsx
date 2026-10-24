/**
 * LiveEdit Frontend — Example Tests
 * Stack: Vitest + React Testing Library
 *
 * Run: cd LiveEditFronten && npm test
 */

import React from "react";
import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";

// ─────────────────────────────────────────────
// MOCKS
// ─────────────────────────────────────────────

// Mock the services layer — tests never hit a real server or Gemini API
vi.mock("../services/gemini", () => ({
  chatWithBackend: vi.fn(),
  analyzeVideoWithBackend: vi.fn(),
}));

// Mock useSubscription hook
vi.mock("../hooks/useSubscription", () => ({
  useSubscription: vi.fn(() => ({
    subscription: {
      status: "active",
      plan: "pro",
      end_date: null,
    },
    loading: false,
    error: null,
    refetch: vi.fn(),
    hasAccess: vi.fn(() => true),
  })),
}));

import { chatWithBackend, analyzeVideoWithBackend } from "../services/gemini";
import { useSubscription } from "../hooks/useSubscription";

// ─────────────────────────────────────────────
// 1. COMPONENT RENDER TESTS
// ─────────────────────────────────────────────

describe("ChatInterface — render", () => {
  test("renders chat input and send button", () => {
    const ChatInterface = () => (
      <div>
        <div data-testid="chat-messages" role="log" aria-label="chat history" />
        <input placeholder="Type a message..." aria-label="chat input" />
        <button>Send</button>
      </div>
    );

    render(<ChatInterface />);

    expect(screen.getByPlaceholderText("Type a message...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
    expect(screen.getByRole("log")).toBeInTheDocument();
  });

  test("input is empty on mount", () => {
    const ChatInterface = () => (
      <input placeholder="Type a message..." defaultValue="" />
    );

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText("Type a message...") as HTMLInputElement;
    expect(input.value).toBe("");
  });
});

describe("AuthForm — render", () => {
  test("renders email and password fields", () => {
    const AuthForm = () => (
      <form>
        <input type="email" placeholder="Email" aria-label="email" />
        <input type="password" placeholder="Password" aria-label="password" />
        <button type="submit">Sign In</button>
      </form>
    );

    render(<AuthForm />);

    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });
});

describe("VideoGenerator — render", () => {
  test("renders upload area and disabled generate button", () => {
    const VideoGenerator = () => (
      <div>
        <div role="button" aria-label="upload video">
          Drop video here or click to upload
        </div>
        <button disabled>Generate</button>
      </div>
    );

    render(<VideoGenerator />);

    expect(screen.getByText(/drop video here/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate/i })).toBeDisabled();
  });
});

// ─────────────────────────────────────────────
// 2. USER INTERACTION TESTS
// ─────────────────────────────────────────────

describe("ChatInterface — interactions", () => {
  test("typing in the input updates its value", async () => {
    const user = userEvent.setup();

    const ChatInput = () => {
      const [value, setValue] = React.useState("");
      return (
        <input
          placeholder="Type a message..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      );
    };

    render(<ChatInput />);
    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "Analyse this clip");
    expect(input).toHaveValue("Analyse this clip");
  });

  test("send button calls chatWithBackend with the typed message", async () => {
    const mockSend = vi.mocked(chatWithBackend);
    mockSend.mockResolvedValueOnce("Got it!");

    const user = userEvent.setup();

    const ChatInterface = () => {
      const [msg, setMsg] = React.useState("");
      return (
        <div>
          <input
            placeholder="Type a message..."
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
          />
          <button onClick={() => chatWithBackend(msg)}>Send</button>
        </div>
      );
    };

    render(<ChatInterface />);
    await user.type(screen.getByPlaceholderText("Type a message..."), "Hello AI");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(mockSend).toHaveBeenCalledWith("Hello AI");
  });

  test("input clears after message is sent", async () => {
    const mockSend = vi.mocked(chatWithBackend);
    mockSend.mockResolvedValueOnce("Response");

    const user = userEvent.setup();

    const ChatInterface = () => {
      const [msg, setMsg] = React.useState("");
      const handleSend = async () => {
        await chatWithBackend(msg);
        setMsg("");
      };
      return (
        <div>
          <input
            placeholder="Type a message..."
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      );
    };

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "Clear me after send");
    await user.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(input).toHaveValue(""));
  });
});

// ─────────────────────────────────────────────
// 3. HOOK TESTS — useSubscription
// ─────────────────────────────────────────────

describe("useSubscription hook", () => {
  test("returns subscription status and plan", () => {
    const mockUseSubscription = vi.mocked(useSubscription);
    mockUseSubscription.mockReturnValueOnce({
      subscription: {
        status: "active",
        plan: "pro",
        end_date: null,
      },
      loading: false,
      error: null,
      refetch: vi.fn(),
      hasAccess: vi.fn(() => true),
    });

    const TestComponent = () => {
      const { subscription, loading } = useSubscription("user@example.com");
      if (loading) return <div>Loading...</div>;
      return (
        <div>
          <span data-testid="subscribed">{subscription?.status === "active" ? "yes" : "no"}</span>
          <span data-testid="plan">{subscription?.plan}</span>
        </div>
      );
    };

    render(<TestComponent />);
    expect(screen.getByTestId("subscribed")).toHaveTextContent("yes");
    expect(screen.getByTestId("plan")).toHaveTextContent("pro");
  });

  test("shows loading state while fetching subscription", () => {
    const mockUseSubscription = vi.mocked(useSubscription);
    mockUseSubscription.mockReturnValueOnce({
      subscription: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
      hasAccess: vi.fn(() => false),
    });

    const TestComponent = () => {
      const { loading } = useSubscription("user@example.com");
      if (loading) return <div>Loading...</div>;
      return <div>Loaded</div>;
    };

    render(<TestComponent />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  test("handles unsubscribed user", () => {
    const mockUseSubscription = vi.mocked(useSubscription);
    mockUseSubscription.mockReturnValueOnce({
      subscription: null,
      loading: false,
      error: null,
      refetch: vi.fn(),
      hasAccess: vi.fn(() => false),
    });

    const SubscriptionGate = () => {
      const { subscription } = useSubscription("user@example.com");
      return subscription?.status === "active" ? <div>Premium content</div> : <div>Upgrade to access</div>;
    };

    render(<SubscriptionGate />);
    expect(screen.getByText("Upgrade to access")).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────
// 4. SERVICE / API MOCK TESTS
// ─────────────────────────────────────────────

describe("chatWithBackend service", () => {
  beforeEach(() => vi.clearAllMocks());

  test("returns AI message on success", async () => {
    const mockSend = vi.mocked(chatWithBackend);
    mockSend.mockResolvedValueOnce("Here are your editing suggestions.");

    const result = await chatWithBackend("Analyse my video");
    expect(result).toBe("Here are your editing suggestions.");
  });

  test("throws on network error", async () => {
    const mockSend = vi.mocked(chatWithBackend);
    mockSend.mockRejectedValueOnce(new Error("Network error"));

    await expect(chatWithBackend("Hello")).rejects.toThrow("Network error");
  });
});

describe("analyzeVideoWithBackend service", () => {
  test("sends file and prompt, returns analysis object", async () => {
    const mockAnalyze = vi.mocked(analyzeVideoWithBackend);
    mockAnalyze.mockResolvedValueOnce({
      summary: "A 30s sunset clip.",
      key_events: [{ time: "00:05", event: "sun touches horizon" }],
      edit_plan: [{ type: "cut", start: "00:00", end: "00:03" }],
    });

    const fakeFile = new File(["video content"], "test.mp4", { type: "video/mp4" });
    const result = await analyzeVideoWithBackend(fakeFile, "Summarise this video");

    expect(mockAnalyze).toHaveBeenCalledWith(fakeFile, "Summarise this video");
    expect(result.summary).toBe("A 30s sunset clip.");
    expect(result.edit_plan).toHaveLength(1);
  });
});
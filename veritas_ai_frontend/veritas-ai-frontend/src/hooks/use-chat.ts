import { useState, useCallback } from "react";
import {
  Message,
  ChatState,
  BackendPromptRequest,
  BackendPromptResponse,
  BackendErrorResponse,
} from "@/types";
import { generateId } from "@/lib/utils";

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
  });

  const addMessage = useCallback(
    (content: string, role: "user" | "assistant") => {
      const message: Message = {
        id: generateId(),
        content,
        role,
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, message],
      }));

      return message;
    },
    []
  );

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message to chat
      addMessage(content, "user");

      // Set loading state
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        // Prepare request for backend
        const promptRequest: BackendPromptRequest = {
          prompt: content,
          temperature: 0.7,
        };

        // Send request to our Next.js API endpoint that will proxy to Django backend
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(promptRequest),
        });

        const data = await response.json();

        if (!response.ok) {
          // Handle error response
          const errorData = data as BackendErrorResponse;
          throw new Error(errorData.error || "Failed to get response");
        }

        // Handle successful response
        const responseData = data as BackendPromptResponse;

        // Add AI response to chat
        addMessage(responseData.response, "assistant");

        // Update state
        setState((prev) => ({ ...prev, isLoading: false }));
      } catch (error) {
        // Handle fetch or processing errors
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error
              ? error.message
              : "An unknown error occurred",
        }));
      }
    },
    [addMessage]
  );

  const clearChat = useCallback(() => {
    setState({ messages: [], isLoading: false, error: null });
  }, []);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    sendMessage,
    clearChat,
  };
}

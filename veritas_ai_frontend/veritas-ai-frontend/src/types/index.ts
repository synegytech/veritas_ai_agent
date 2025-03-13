export type Message = {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
};

export type ChatState = {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
};

export type BackendPromptRequest = {
  prompt: string;
  model?: string;
  temperature?: number;
  max_output_tokens?: number;
};

export type BackendPromptResponse = {
  response: string;
  model: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
};

export type BackendErrorResponse = {
  error: string;
  details?: Record<string, any>;
};

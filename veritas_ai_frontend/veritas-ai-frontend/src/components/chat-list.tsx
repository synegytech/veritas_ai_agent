import { useRef, useEffect } from "react";
import { Message } from "@/types";
import { ChatBubble } from "@/components/chat-bubble";
import { Loader2 } from "lucide-react";

interface ChatListProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatList({ messages, isLoading }: ChatListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <h3 className="text-2xl font-semibold mb-2">Welcome to Veritas AI</h3>
          <p className="text-muted-foreground text-sm max-w-md">
            Start a conversation with the AI assistant powered by Google's
            Gemini models.
          </p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
        </>
      )}

      {isLoading && (
        <div className="flex items-center gap-2 p-4">
          <Loader2 className="h-4 w-4 animate-spin" />
          <p className="text-sm text-muted-foreground">
            Generating response...
          </p>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

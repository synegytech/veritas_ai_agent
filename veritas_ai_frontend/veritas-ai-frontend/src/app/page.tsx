"use client";

import { useChat } from "@/hooks/use-chat";
import { ChatHeader } from "@/components/chat-header";
import { ChatList } from "@/components/chat-list";
import { ChatInput } from "@/components/chat-input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { useEffect } from "react";

export default function ChatPage() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();

  // Show error toast when there's an error
  useEffect(() => {
    if (error) {
      toast.error("Error", {
        description: error,
      });
    }
  }, [error]);

  return (
    <div className="flex flex-col h-screen max-h-screen">
      <div className="flex-1 container mx-auto max-w-4xl py-4">
        <Card className="h-full flex flex-col">
          <ChatHeader onClearChat={clearChat} />
          <ChatList messages={messages} isLoading={isLoading} />
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </Card>
      </div>
    </div>
  );
}

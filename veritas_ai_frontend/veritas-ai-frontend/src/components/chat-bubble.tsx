import { cn, formatTime } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import { Message } from "@/types";

interface ChatBubbleProps {
  message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full gap-3 p-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <Avatar className="h-8 w-8">
          <div className="bg-primary text-primary-foreground flex h-8 w-8 items-center justify-center rounded-full">
            AI
          </div>
        </Avatar>
      )}

      <div
        className={cn(
          "flex flex-col max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "rounded-lg px-4 py-2",
            isUser ? "bg-primary text-primary-foreground" : "bg-muted"
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
        <span className="text-xs text-muted-foreground mt-1">
          {formatTime(message.timestamp)}
        </span>
      </div>

      {isUser && (
        <Avatar className="h-8 w-8">
          <div className="bg-zinc-800 text-zinc-50 flex h-8 w-8 items-center justify-center rounded-full">
            U
          </div>
        </Avatar>
      )}
    </div>
  );
}

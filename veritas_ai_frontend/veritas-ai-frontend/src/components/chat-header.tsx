import { Button } from "@/components/ui/button";
import { Trash2, Settings } from "lucide-react";

interface ChatHeaderProps {
  onClearChat: () => void;
}

export function ChatHeader({ onClearChat }: ChatHeaderProps) {
  return (
    <div className="border-b p-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-semibold">V</span>
        </div>
        <div>
          <h2 className="font-semibold">Veritas AI Assistant</h2>
          <p className="text-xs text-muted-foreground">
            Powered by Google Gemini
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <Button variant="outline" size="icon" title="Settings">
          <Settings className="h-4 w-4" />
          <span className="sr-only">Settings</span>
        </Button>
        <Button
          variant="outline"
          size="icon"
          title="Clear chat"
          onClick={onClearChat}
        >
          <Trash2 className="h-4 w-4" />
          <span className="sr-only">Clear chat</span>
        </Button>
      </div>
    </div>
  );
}

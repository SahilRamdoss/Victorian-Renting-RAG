"use client"

import { useChat } from "@/hooks/use-chat"
import { ChatInput } from "@/components/ChatbotInterface/chat-input"
import { ChatMessages } from "@/components/ChatbotInterface/chat-messages"

export function ChatInterface() {
  const { messages, isLoading, error, sendMessage } = useChat()

  return (
    <section className="flex h-full w-full flex-col items-center bg-black">
      <div className="min-h-0 w-full flex-1 overflow-y-auto ps-10 pe-10">
        <ChatMessages messages={messages} isLoading={isLoading} error={error} />
      </div>
      <div className="w-full pb-10">
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </section>
  )
}
"use client"

import * as React from "react"
import type { ChatMessage } from "@/hooks/use-chat"

type ChatMessagesProps = {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
}

export function ChatMessages({ messages, isLoading, error }: ChatMessagesProps) {
  const bottomRef = React.useRef<HTMLDivElement>(null)

  // Keep the newest message in view
  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 py-6">
      {messages.map((message) =>
        message.role === "user" ? (
          <div
            key={message.id}
            className="max-w-[80%] self-end whitespace-pre-wrap rounded-3xl bg-zinc-800 px-5 py-3 text-zinc-100"
          >
            {message.content}
          </div>
        ) : (
          <div key={message.id} className="whitespace-pre-wrap text-zinc-100">
            {message.content}
          </div>
        )
      )}

      {isLoading && <div className="animate-pulse text-zinc-500">Thinking…</div>}
      {error && <div className="text-red-400">{error}</div>}

      <div ref={bottomRef} />
    </div>
  )
}
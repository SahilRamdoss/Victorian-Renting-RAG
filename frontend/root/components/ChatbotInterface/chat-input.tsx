"use client"

import * as React from "react"
import { ArrowUpIcon } from "lucide-react"

import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from "@/components/ui/input-group"

type ChatInputProps = {
  onSend: (text: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [text, setText] = React.useState("")
  const formRef = React.useRef<HTMLFormElement>(null)
  const canSend = text.trim().length > 0 && !disabled

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canSend) return
    onSend(text.trim())
    setText("")
  }

  return (
    <form ref={formRef} onSubmit={onSubmit} className="mx-auto w-full ps-8 pe-8">
      <InputGroup className="rounded-3xl shadow-sm">
        <InputGroupTextarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Ask anything"
          className="max-h-48 p-4"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault()
              formRef.current?.requestSubmit()
            }
          }}
        />
        <InputGroupAddon align="block-end">
          <InputGroupButton
            type="submit"
            size="icon-sm"
            variant="default"
            className="ml-auto rounded-full"
            disabled={!canSend}
            aria-label="Send"
          >
            <ArrowUpIcon />
          </InputGroupButton>
        </InputGroupAddon>
      </InputGroup>
    </form>
  )
}
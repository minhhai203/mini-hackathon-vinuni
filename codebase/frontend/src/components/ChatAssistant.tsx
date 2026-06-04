"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import type { ChatCard, ChatMessage, ChatResponse } from "@/lib/chat";

const starterPrompts = [
  "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em và nghỉ biển.",
  "Đi Nha Trang, ưu tiên nghỉ biển và vui chơi cho trẻ em.",
  "Tôi muốn villa, voucher dùng được chắc chắn và còn phòng tối nay không?",
];

export function ChatAssistant() {
  const [isOpen, setIsOpen] = useState(true);
  const [profile, setProfile] = useState<Record<string, unknown>>({});
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Xin chào, mình là Vinpearl AI Assistant. Hãy cho mình biết điểm đến, nhóm đi, ngày đi, ngân sách và ưu tiên. Nếu bạn chưa chắc ngân sách/ngày, mình vẫn có thể gợi ý trước rồi hỏi thêm.",
    },
  ]);
  const [suggestions, setSuggestions] = useState(starterPrompts);
  const [pending, setPending] = useState(false);
  const [draft, setDraft] = useState("");
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const themeClass = useMemo(() => {
    const latestAssistant = [...messages].reverse().find((message) => message.context?.weather?.ui_theme);
    return latestAssistant?.context?.weather?.ui_theme ?? "theme-default";
  }, [messages]);

  async function sendMessage(message: string) {
    const cleanMessage = message.trim();
    if (!cleanMessage || pending) return;

    const userMessage: ChatMessage = { role: "user", content: cleanMessage };
    setMessages((current) => [...current, userMessage]);
    setDraft("");
    setPending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: cleanMessage,
          profile,
          history: messages.slice(-8).map((item) => ({ role: item.role, content: item.content })),
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat API returned ${response.status}`);
      }

      const data = (await response.json()) as ChatResponse;
      setProfile(data.profile);
      setSuggestions(data.suggestions.length ? data.suggestions : starterPrompts);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: buildAssistantSummary(data),
          cards: data.cards,
          context: data.context,
          confidence: data.confidence,
          safetyNotice: data.safety_notice,
        },
      ]);
      requestAnimationFrame(() => chatEndRef.current?.scrollIntoView({ behavior: "smooth" }));
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: "Backend chưa phản hồi. Hãy chắc là FastAPI đang chạy ở port 8000 rồi thử lại.",
        },
      ]);
    } finally {
      setPending(false);
    }
  }

  function submitForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(draft);
  }

  return (
    <div className={`assistant-shell ${themeClass}`}>
      <button className="assistant-fab" onClick={() => setIsOpen((value) => !value)} type="button">
        {isOpen ? "×" : "AI"}
      </button>

      {isOpen && (
        <aside className="assistant-panel" aria-label="Vinpearl AI Assistant">
          <header className="assistant-header">
            <div>
              <strong>Vinpearl AI Assistant</strong>
              <span>Gợi ý nghỉ dưỡng + vui chơi cá nhân hóa</span>
            </div>
            <button onClick={() => setIsOpen(false)} type="button" aria-label="Đóng trợ lý">
              ×
            </button>
          </header>

          <div className="assistant-messages">
            {messages.map((message, index) => (
              <article className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
                <p>{message.content}</p>
                {message.context && <ContextStrip context={message.context} />}
                {message.cards?.length ? <RecommendationCards cards={message.cards} /> : null}
                {message.safetyNotice && <p className="safety-note">{message.safetyNotice}</p>}
              </article>
            ))}
            {pending && (
              <article className="chat-message assistant">
                <p>Đang gọi agent tools để lọc option phù hợp...</p>
              </article>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="assistant-suggestions">
            {suggestions.slice(0, 3).map((suggestion) => (
              <button key={suggestion} type="button" onClick={() => void sendMessage(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>

          <form className="assistant-input" onSubmit={submitForm}>
            <input
              aria-label="Nhập câu hỏi cho Vinpearl AI"
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ví dụ: đi Phú Quốc 3 ngày, gia đình có bé..."
              value={draft}
            />
            <button disabled={pending} type="submit">
              Gửi
            </button>
          </form>
        </aside>
      )}
    </div>
  );
}

function RecommendationCards({ cards }: { cards: ChatCard[] }) {
  return (
    <div className="recommendation-list">
      {cards.map((card, index) => (
        <section className="recommendation-card" key={card.option}>
          {card.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img alt={card.option} src={`/${card.image_url}`} />
          )}
          <div className="recommendation-body">
            <span className="eyebrow">
              #{index + 1} · {card.option_type} · {card.destination}
            </span>
            <h4>{card.option}</h4>
            <div className="badge-row">
              {card.context_badges.map((badge) => (
                <span key={badge}>{badge}</span>
              ))}
            </div>
            <p>{card.why_it_fits}</p>
            <p>
              <strong>Trade-off:</strong> {card.trade_off.join(" ")}
            </p>
            <small>Confidence: {card.confidence}</small>
          </div>
        </section>
      ))}
    </div>
  );
}

function ContextStrip({ context }: { context: ChatResponse["context"] }) {
  const positives = context.reviews?.positive?.slice(0, 2).join(", ");

  return (
    <div className="context-strip">
      {context.weather?.condition_summary && <span>{context.weather.condition_summary}</span>}
      {positives && <span>Review signal: {positives}</span>}
    </div>
  );
}

function buildAssistantSummary(data: ChatResponse) {
  if (data.cards.length) {
    const prefix = data.needs_followup
      ? "Mình có thể gợi ý trước dù còn thiếu vài thông tin."
      : "Đây là top 3 option match nhất theo profile hiện tại.";
    return `${prefix} Độ tin cậy tổng: ${data.confidence}.`;
  }

  if (data.needs_followup) {
    return data.suggestions.length
      ? `Mình cần thêm thông tin để match tốt hơn: ${data.suggestions.join(" ")}`
      : "Mình cần thêm điểm đến, ngày đi, nhóm đi, ngân sách hoặc ưu tiên để gợi ý tốt hơn.";
  }

  return "Mình đã xử lý yêu cầu của bạn.";
}

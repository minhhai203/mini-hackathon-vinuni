export type ChatCard = {
  option: string;
  option_type: string;
  destination: string | null;
  image_url?: string | null;
  context_badges: string[];
  best_for: string[];
  why_it_fits: string;
  trade_off: string[];
  confidence: string;
  next_step: string;
};

export type ChatContext = {
  weather?: {
    condition_summary?: string;
    temperature_c?: number | null;
    ui_theme?: string;
  };
  reviews?: {
    positive?: string[];
    watchouts?: string[];
  };
};

export type ChatResponse = {
  reply: string;
  profile: Record<string, unknown>;
  suggestions: string[];
  cards: ChatCard[];
  confidence: string;
  needs_followup: boolean;
  used_tools: string[];
  safety_notice?: string | null;
  ui_theme: string;
  context: ChatContext;
  data_source?: string | null;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  cards?: ChatCard[];
  context?: ChatContext;
  confidence?: string;
  safetyNotice?: string | null;
};

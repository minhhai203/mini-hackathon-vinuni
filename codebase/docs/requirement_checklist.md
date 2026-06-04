# Requirement Checklist

## Done

- Basic Vinpearl clone UI for web.
- Chatbot assistant embedded in the web UI.
- Chatbot keeps user profile across turns and auto-fills known fields.
- Chatbot asks follow-up questions when core information is missing.
- Chatbot can still recommend when budget/date is uncertain if destination and priority are clear.
- Top 3 ranked recommendations for stay/activity options.
- Recommendation cards include image, type, destination, badges, trade-off, confidence, and policy guard.
- Data includes Vinpearl stay options plus in/out-of-campus activity suggestions.
- Agent tool registry includes source discovery, Vinpearl crawler, extraction, ranking, formatting, safety, evaluation, weather/news/review mock context.
- UI theme changes lightly by destination/weather context.
- Risk handling for realtime price, availability, voucher, cancellation, and refund claims.
- Tests for chatbot service, API endpoint, crawler wrapper, ranking/extraction/eval tools.

## Mocked For Prototype

- Weather context is mock data.
- News/trend context is mock data.
- Review signals are mock summaries.
- Resort/package/activity data is local mock data.
- Images reuse existing local static assets.

## Not In Scope

- Mobile app clone.
- Real booking/payment.
- Real login or MyVinpearl integration.
- Realtime price or room availability API.
- Real voucher/cancellation confirmation.
- Live news/weather/review API.

"""Stream AI-powered financial analysis in real-time."""

from vectrade import VecTrade

vt = VecTrade()

# Stream analysis — prints tokens as they arrive
for chunk in vt.ai.stream("Analyze TSLA earnings outlook for Q3 2026"):
    print(chunk.text, end="", flush=True)

print()  # newline after stream completes

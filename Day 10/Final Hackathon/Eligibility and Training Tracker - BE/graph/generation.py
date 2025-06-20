def generate_answer(query, contexts):
    prompt = build_prompt(query, contexts)
    return call_gemini(prompt, model="gemini‑1.5‑flash")
def validate_answer(ans, contexts):
    return "I'm confident" in ans  # or LLM-based self-check

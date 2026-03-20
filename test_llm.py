import ollama

try:
    print("Calling tinyllama...")

    response = ollama.chat(
        model="tinyllama",
        messages=[{"role": "user", "content": "What is BAJA SAE?"}],
    )

    print("SUCCESS ✅")
    print(response["message"]["content"])

except Exception as e:
    print("ERROR ❌:", e)
from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="gemma2-9b-it",
    messages=[
        {
            "role": "system",
            "content": "you are helpful assistant"
        },
        {
            "role": "user",
            "content": "who you are?"
        },
        {
            "role": "assistant",
            "content": "Hello! I am Gemma, an open-weights AI assistant.\n\nThat means I'm a large language model trained to be helpful and informative, and my weights are publicly available. This allows anyone to access, study, and modify me.\n\nI can do many things, like:\n\n* **Answer your questions:** I can provide information on a wide range of topics, even if they are open ended, challenging, or strange.\n\n* **Generate creative content:**\n\nI can write stories, poems, and even code.\n\n* **Summarize text:**\n\nI can condense large amounts of information into shorter, easier-to-understand summaries.\n* **Translate languages:** I can translate text between multiple languages.\n\nI am still under development, but I am learning new things every day. My goal is to be a helpful and informative resource for everyone.\n\nWhat can I do for you today?\n"
        }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")

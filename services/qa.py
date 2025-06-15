
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.getenv('TOGETHER_API_KEY')
)


def answer_question(user_message: str,context: str, chat_history: list) -> tuple:
    try:
        system_prompt = system_prompt = (
                    "You are Lextorah Tutor, a Socratic academic assistant. "
                    "Guide students by asking critical thinking questions rather than giving direct answers. "
                    "Use the provided information only if it is helpful to answer the student's question. "
                    "**If the context is not helpful or not related, ignore it and answer normally.** "
                    "Do not mention the word 'context'. "
                    f"\n\n### Information:\n{context}\n"
                )
    
        # Add user's new question to history
        chat_history.append({"role": "user", "content":user_message})

        # Build special system prompt INCLUDING context
        
        print(chat_history, "1")
        # Replace the first system message (dynamic system prompt now)
        chat_history[0] =  {"role": "system", "content": system_prompt}
        print(chat_history)

        # Call Together API
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=chat_history,
            max_tokens=512,
            temperature=0.5
        )

        assistant_message = completion.choices[0].message.content.strip()

        # Append assistant reply
        chat_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message, chat_history

    except Exception as e:
        return f"Error: {e}", chat_history
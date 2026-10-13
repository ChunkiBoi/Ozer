import openai
from flask import g
from flask_login import current_user
from google import genai
from groq import Groq, RateLimitError


def save_user_message(chat_id, message):
    g.db.execute(
        """
        INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)
        """,
        (chat_id, "user", message)
    )
    g.db.commit()
    return


def save_bot_response(chat_id, response):
    g.db.execute(
        """
        INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)
        """,
        (chat_id, "bot", response)
    )
    g.db.commit()
    return


groq_client = Groq()
class GroqHandler:
    def __init__(self, client, settings=None):
        self.client = client
        self.settings = settings

    def stream(self, message, settings=None):
        if settings is None:
            settings = self.settings

        try:  
            if settings["model"] == "openai/gpt-oss-20b" or settings["model"] == "openai/gpt-oss-120b":
                effort = "medium"
            else:
                effort = "default"

            completion = self.client.chat.completions.create(
                model=settings["model"],
                messages=message,
                temperature=0.6,
                max_completion_tokens=1000,
                top_p=0.95,
                reasoning_effort=effort,
                stream=True,
                stop=None,
            )

            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
            print(response)
            try:
                if settings["chat_id"]:
                    save_bot_response(settings["chat_id"], response)
            except:
                pass
        except RateLimitError:
            yield "**[Error: Groq API rate limit reached for the current model. Please wait a moment before trying again, or choose another model.]**"

    def respond(self, message, settings=None):
        if settings is None:
            settings = self.settings

        if settings["model"] == "openai/gpt-oss-20b" or settings["model"] == "openai/gpt-oss-120b":
            effort = "medium"
        else:
            effort = "default"

        completion = self.client.chat.completions.create(
            model=settings["model"],
            messages=[
                {"role": "system", "content": settings["sys_prompt"]},
                {"role": "user", "content": message},
            ],
            temperature=0.6,
            max_completion_tokens=1000,
            top_p=0.95,
            reasoning_effort=effort,
            stream=False,
            stop=None,
        )

        response_text = completion.choices[0].message.content
        print()
        print(response_text)
        return response_text

    def get_context(self, message, settings=None):
        if settings is None:
            settings = self.settings

        msg_list = g.db.execute(
            """
            SELECT sender, content FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            (settings["chat_id"],)
        )
        context_window = []
        for msg in msg_list:
            if msg["sender"] == "user":
                entry = {"role": msg["sender"], "content": msg["content"]}
            elif msg["sender"] == "bot":
                entry = {"role": "assistant", "content": msg["content"]}
            context_window.insert(0, entry)
        if settings["sys_prompt"] != "None":
            context_window.insert(0, {"role": "system", "content": settings["sys_prompt"]})

        return context_window
                    

def generate_chat_name(payload_message, payload_settings):
    groq_bot = GroqHandler(
        client=groq_client,
        settings={
            "model": payload_settings["model"],
            "sys_prompt": "Your sole purpose is to generate a very short 'chat title' based on your summarization of the received message."
        }
    )
    chat_name = groq_bot.respond(payload_message)
    return chat_name


def save_chat(payload):
    settings = payload["settings"]

    user_id = current_user.id
    chat_name = generate_chat_name(payload["message"], settings)
    model = settings["model"]
    sys_prompt = settings["sys_prompt"]

    g.db.execute(
        """
        INSERT INTO chats (user_id, name, model, sys_prompt)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, chat_name, model, sys_prompt)
    )
    g.db.commit()

    chat_id = g.db.execute(
        """
        SELECT id FROM chats
        WHERE user_id = ?
        AND name = ?
        ORDER BY id DESC
        """,
        (user_id, chat_name)
    ).fetchone()

    return chat_id[0]


def get_sys_prompt():
    sys_prompt = g.db.execute(
        """
        SELECT default_sys_prompt FROM settings
        WHERE user_id = ?
        """,
        (current_user.id,)
    ).fetchone()

    if sys_prompt is None or sys_prompt[0] is None:
        sys_prompt = " "
        return sys_prompt
    
    return sys_prompt[0]


def get_chat_list():
    chat_list = g.db.execute(
        """
        SELECT id, name, model, sys_prompt FROM chats
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (current_user.id,)
    )

    return chat_list


def get_messages(chat_id):
    message_list = g.db.execute(
        """
        SELECT sender, content FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp
        """,
        (chat_id,)
    )

    return message_list
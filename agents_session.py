# agents_session.py
from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager
import logging
import asyncio


class BotSession:
    def __init__(self, config):
        self.bot = None
        self.chat_id = None
        self.config = config
        self.session_started = False

        # Agents
        self.user_proxy = UserProxyAgent(
            name="Nicolas",
            human_input_mode="NEVER",  # On contrôle via Telegram
            is_termination_msg=lambda x: "exit" in x.get("content", "").lower(),
            code_execution_config={"use_docker": False},
        )

        self.planner = AssistantAgent(
            name="planner",
            llm_config=config,
            system_message="Ton but est d'aider à organiser le plan d'un article de blog comme si tu étais un étudiant en école d'ingé.",
        )

        self.writer = AssistantAgent(
            name="writer",
            llm_config=config,
            system_message="Ton but est de rédiger des articles de blog comme si tu étais un étudiant en école d'ingé, tu aimes bien partager ce que tu fais",
        )

        # self.groupchat = GroupChat(
        #     agents=[self.user_proxy, self.planner, self.writer],
        #     messages=[],
        #     max_round=5,
        # )

        self.groupchat = GroupChat(
            agents=[self.user_proxy, self.planner, self.writer],
            messages=[],
            max_round=2,
        )

        self.manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=config,
        )

    def set_telegram_context(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    def send_to_telegram(self, message):
        """Utilisé par les agents pour répondre sur Telegram"""
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = str(message)

        if content and self.bot and self.chat_id:
            logging.info(f"[Telegram] Message à envoyer : {content}")
            asyncio.create_task(
                self.bot.send_message(chat_id=self.chat_id, text=content)
            )

    def register_reply_handler(self):
        """Réponse des autres agents relayée vers Telegram"""

        def reply_handler(recipient, messages, sender, config):
            last_msg = messages[-1]["content"] if messages else ""
            if last_msg:
                self.send_to_telegram(last_msg)
            return False, None  # Pas de réponse auto du user_proxy

        self.user_proxy.register_reply(lambda sender: True, reply_handler)

    def handle_user_message(self, message: str):
        logging.info(f"[Telegram] Message à traiter : {message}")

        # Envoie le message utilisateur à l’agent (planner ici, ou autre)
        self.user_proxy.send(
            message={"content": message},
            recipient=self.manager,  # ou self.manager si GroupChat
            request_reply=True,
        )

        # Récupère la dernière réponse (si elle est synchronisée immédiatement)
        last_reply = self.planner.last_message()["content"]

        # Envoie dans Telegram
        asyncio.create_task(
            self.bot.send_message(chat_id=self.chat_id, text=last_reply)
        )

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# CONFIGURATION LLM
config = {
    "config_list": [
        {"model": "gpt-4", "api_key": api_key}
    ],  # remplace par ton API key ou mets dans .env
}

# 👤 Toi, en agent interactif
user = UserProxyAgent(
    name="nicolas",
    human_input_mode="ALWAYS",
    code_execution_config={"use_docker": False},
)

# 📋 Agent qui propose un plan d’article
planner = AssistantAgent(
    name="planner",
    llm_config=config,
    system_message="Tu aides à organiser les idées. Propose un plan structuré pour un article de blog à partir des idées de Nicolas. Tu dois poser des questions si besoin avant de rédiger quoi que ce soit.",
)

# 🖋️ Agent qui rédige en markdown
writer = AssistantAgent(
    name="writer",
    llm_config=config,
    system_message="Tu es un rédacteur de blog qui écrit dans un style clair, personnel et fluide. Une fois que le plan est validé, écris un article complet en markdown.",
)

# 👥 Création du chat entre les agents
chat = GroupChat(
    agents=[user, planner, writer],
    messages=[],
    max_round=20,
)

manager = GroupChatManager(groupchat=chat, llm_config=config)

# 🟢 Déclenche l’échange
user.initiate_chat(
    manager,
    message="Voici la transcription de mon vocal : 'J'aimerais parler de mon expérience avec la fabrication d'un jeu connecté et comment j'ai géré les défis techniques.'",
)

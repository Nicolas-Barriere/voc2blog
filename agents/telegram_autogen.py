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


def handle_transcription(transcription: str):
    """Lance une session AutoGen avec la transcription fournie"""

    # Agent utilisateur : ne demande pas d'entrée humaine
    user_proxy = UserProxyAgent(
        name="nicolas",
        human_input_mode="ALWAYS",
        is_termination_msg=lambda x: "exit" in x.get("content", "").lower(),
        code_execution_config={"use_docker": False},
    )

    # Agent planificateur
    planner = AssistantAgent(
        name="planner",
        llm_config=config,
        system_message="Tu aides à organiser les idées. Propose un plan structuré pour un article de blog à partir des idées de Nicolas. Pose des questions si besoin avant de rédiger quoi que ce soit.",
    )

    # Agent rédacteur
    writer = AssistantAgent(
        name="writer",
        llm_config=config,
        system_message="Tu es un rédacteur de blog qui écrit dans un style clair, personnel et fluide. Une fois que le plan est validé, écris un article complet en markdown.",
    )

    # Chat de groupe AutoGen
    groupchat = GroupChat(
        agents=[user_proxy, planner, writer],
        messages=[],
        max_round=15,
    )

    manager = GroupChatManager(groupchat=groupchat, llm_config=config)

    # Lancer la discussion
    user_proxy.initiate_chat(
        manager,
        message=f"Voici la transcription de mon vocal : '{transcription}'",
    )

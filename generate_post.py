from openai import OpenAI

client = OpenAI()


def generate_post(transcription):
    response = client.responses.create(
        model="gpt-4o",
        instructions="Tu es un assistant éditorial. Prends cette consigne orale et transforme-la en un article de blog structuré (introduction, paragraphes, conclusion si nécessaire). Le style doit être fluide, clair et adapté à un blog technique personnel. Retourne uniquement le contenu markdown, avec des titres H2 et gras si besoin.",
        input=transcription,
    )
    return response.output_text

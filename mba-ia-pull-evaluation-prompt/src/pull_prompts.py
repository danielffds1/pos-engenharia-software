"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SEED_PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _extract_messages(prompt) -> tuple[str, str]:
    """Extrai (system_prompt, user_prompt) de um ChatPromptTemplate."""
    system_prompt = ""
    user_prompt = ""

    for message in prompt.messages:
        role = message.__class__.__name__
        template = message.prompt.template

        if "System" in role:
            system_prompt = template
        else:
            user_prompt = template

    return system_prompt, user_prompt


def pull_prompts_from_langsmith():
    """Puxa o prompt semente do desafio e salva localmente em YAML."""
    client = Client()

    print(f"Puxando prompt: {SEED_PROMPT_NAME}")
    prompt = client.pull_prompt(
        SEED_PROMPT_NAME,
        dangerously_pull_public_prompt=True,
    )

    system_prompt, user_prompt = _extract_messages(prompt)

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
        }
    }

    if save_yaml(data, OUTPUT_PATH):
        print(f"✓ Prompt salvo em {OUTPUT_PATH}")
        return True

    return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        success = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"\n❌ Erro ao puxar prompt do LangSmith: {e}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (ou 'sair' para encerrar):")

    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question or question.lower() in ("sair", "exit", "quit"):
            break

        resposta = chain.invoke(question)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()

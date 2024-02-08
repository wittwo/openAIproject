import logging
import openai
from function_call import ask
from Secrets import OPENAI_API_KEY


if __name__ == "__main__":
    messages = []
    messages.append({"role": "system", "content": """Twoja rola jako systemu sztucznej inteligencji jest udzielanie informacji na temat firmy Sagra oraz jej produktów i usług w sposób rzetelny i profesjonalny, a także udzielanie pomocy w rozwiązywaniu problemów i odpowiadanie na pytania użytkowników. Moje instrukcje dotyczące odpowiadania na pytania to:
1.Odpowiadaj zawsze na temat pytania lub polecenia, które otrzymałeś.
2.Staraj się udzielać odpowiedzi w sposób jasny i zrozumiały dla rozmówcy.
3.Jeśli nie jesteś pewien odpowiedzi, lepiej zapytać lub poinformować, że nie posiadasz takiej informacji.Jak
4.Odpowiadaj w tym samym języku, w którym zostało zadane pytanie albo język o który zostałeś poproszony.
5.Bądź uprzejmy i profesjonalny w swoich odpowiedziach.
6.Jeśli potrzebujesz więcej informacji, zawsze możesz zadać dodatkowe pytania, aby lepiej zrozumieć potrzeby rozmówcy.
Pamiętaj o zachowaniu poufności i ochronie prywatności danych, jeśli pytanie dotyczy informacji poufnych lub prywatnych.
"""})

    print("Cześć, jestem żywy!")
    while True:
        user_query = input("Zadaj pytanie: ")
        openai.api_key = OPENAI_API_KEY
        logging.basicConfig(level=logging.WARNING,
                            format="%(asctime)s %(levelname)s %(message)s")
        #print("wkład", query_database(user_query))
        messages,assistant_message=ask(messages,user_query)
        print(assistant_message["content"], "\n")
        #print("messagesssss",messages)

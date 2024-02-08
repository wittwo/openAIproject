import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
import logging
import openai
from function_call import ask
from Secrets import OPENAI_API_KEY


def on_send(event=None):
    global messages
    user_message = user_input.get()
    if user_message.strip() != "":
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "\nYou: " + user_message + "\n", 'user')
        chat_history.config(state=tk.DISABLED)

        messages, assistant_message = ask(messages, user_message)
        chat_response = assistant_message["content"]

        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "\nChatbot: " + chat_response + "\n", 'chatbot')
        chat_history.config(state=tk.DISABLED)

    user_input.delete(0, tk.END)
    chat_history.see(tk.END)


root = tk.Tk()
root.title("ChatGPT Chat")
root.geometry("400x1000")
root.configure(bg="#1e1e1e")

chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=40, bg="#2e2e2e", fg="white")
chat_history.pack(padx=10, pady=10)
chat_history.tag_config("user", foreground="#ffffff")
chat_history.tag_config("chatbot", foreground="#0dffc2")
chat_history.config(state=tk.DISABLED)

# Create a frame to contain the input box and button
input_frame = ctk.CTkFrame(root, bg_color="#1e1e1e")

input_frame.pack(padx=10, pady=10, fill=tk.X, expand=True)

# Create a label to the left of the input box
label = ctk.CTkLabel(input_frame, text="Ask SDM", bg_color="#2e2e2e", text_color="#ff00e6",corner_radius=450)
label.pack(side=tk.LEFT, padx=0,ipady=5)


# Initialize user input field with doubled width, centralized and focused
user_input = ctk.CTkEntry(input_frame, fg_color="#2e2e2e", text_color="#ff00e6",placeholder_text="CTkEntry")
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
user_input.bind('<Return>', on_send)

# Add a send button with an arrow symbol
send_button = ctk.CTkButton(input_frame, text="→", command=on_send, bg_color="#1E90FF", text_color="white",corner_radius=450)
send_button.pack(side=tk.LEFT, padx=1,ipady=5)

# Set focus on the input field
user_input.focus_set()

messages = []
messages.append({
    "role": "system",
    "content": """Twoja rola jako systemu sztucznej inteligencji jest udzielanie informacji na temat firmy oraz jej produktów i usług w sposób rzetelny i profesjonalny, a także udzielanie pomocy w rozwiązywaniu problemów i odpowiadanie na pytania użytkowników. Moje instrukcje dotyczące odpowiadania na pytania to:
1.Odpowiadaj zawsze na temat pytania lub polecenia, które otrzymałeś.
2.Staraj się udzielać odpowiedzi w sposób jasny i zrozumiały dla rozmówcy.
3.Jeśli nie jesteś pewien odpowiedzi, lepiej zapytać lub poinformować, że nie posiadasz takiej informacji.
4.Odpowiadaj w tym samym języku, w którym zostało zadane pytanie albo język o który zostałeś poproszony.
5.Bądź uprzejmy i profesjonalny w swoich odpowiedziach.
6.Jeśli potrzebujesz więcej informacji, zawsze możesz zadać dodatkowe pytania, aby lepiej zrozumieć potrzeby rozmówcy.
Pamiętaj o zachowaniu poufności i ochronie prywatności danych, jeśli pytanie dotyczy informacji poufnych lub prywatnych.
7. Jeśli pytanie jest nie zrozumiałe, napisz, że nie rozumiesz"""
})

openai.api_key = OPENAI_API_KEY

root.mainloop()
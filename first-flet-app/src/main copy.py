import flet as ft


# --- Mock Data Classes (Required for the application logic) ---

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

class Message:
    def __init__(self, sender_id, content):
        self.sender_id = sender_id
        self.content = content

class Chat:
    def __init__(self, chat_id, participants):
        self.chat_id = chat_id
        self.participants = participants
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

# --- Application Logic ---

class ChatApp:
    def __init__(self):
        self.users = {}
        self.chats = {}
        self.current_user = None
        self.current_chat = None

    def add_user(self, user_id, name):
        self.users[user_id] = User(user_id, name)

    def set_current_user(self, user_id):
        if user_id in self.users:
            self.current_user = self.users[user_id]

    def create_chat(self, chat_id, participant_ids):
        participants = [self.users[pid] for pid in participant_ids if pid in self.users]
        self.chats[chat_id] = Chat(chat_id, participants)

    def set_current_chat(self, chat_id):
        if chat_id in self.chats:
            self.current_chat = self.chats[chat_id]

    def send_message(self, content):
        if self.current_user and self.current_chat:
            message = Message(self.current_user.user_id, content)
            self.current_chat.add_message(message)

# --- Flet UI Components ---

class ChatUI:
    def __init__(self, app_logic, page):
        self.app_logic = app_logic
        self.page = page
        self.chat_list = ft.ListView()
        self.message_list = ft.ListView()
        self.message_input = ft.TextField(hint_text="Type a message...", expand=True)
        self.send_button = ft.IconButton(
         icon=ft.Icons.SEND,  # ✅ CORRECT: Use ft.icons.SEND
         on_click=self.send_message)

    def build(self):
        self.page.title = "Chat Application"
        self.page.add(
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Chats", style="headlineMedium"),
                            self.chat_list,
                        ],
                        width=200,
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        [
                            ft.Text("Messages", style="headlineMedium"),
                            self.message_list,
                            ft.Row(
                                [self.message_input, self.send_button],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            )
        )
        self.page.update()

    def send_message(self, e):
        content = self.message_input.value
        if content:
            self.app_logic.send_message(content)
            self.update_message_list()
            self.message_input.value = ""
            self.page.update()

    def update_message_list(self):
        if self.app_logic.current_chat:
            self.message_list.controls.clear()
            for msg in self.app_logic.current_chat.messages:
                sender_name = self.app_logic.users[msg.sender_id].name
                self.message_list.controls.append(ft.Text(f"{sender_name}: {msg.content}"))
            self.message_list.update()

    def update_chat_list(self):
        self.chat_list.controls.clear()
        for chat_id, chat in self.app_logic.chats.items():
            participant_names = ", ".join([user.name for user in chat.participants])
            chat_button = ft.ElevatedButton(
                text=participant_names,
                on_click=lambda e, cid=chat_id: self.select_chat(cid)
            )
            self.chat_list.controls.append(chat_button)
        self.chat_list.update()

    def select_chat(self, chat_id):
        self.app_logic.set_current_chat(chat_id)
        self.update_message_list()

# --- Main Application Entry Point ---
def main(page: ft.Page):
    app_logic = ChatApp()
    app_logic.add_user("1", "Alice")
    app_logic.add_user("2", "Bob")
    app_logic.set_current_user("1")
    app_logic.create_chat("chat1", ["1", "2"])

    chat_ui = ChatUI(app_logic, page)
    chat_ui.build()
    chat_ui.update_chat_list()

ft.app(target=main)
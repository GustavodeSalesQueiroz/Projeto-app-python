import flet as ft


# --- Mock Data Classes (Required for the application logic) ---

class Board:
    """Represents a Trello Board."""
    def __init__(self, app, store, name, page):
        self.app = app
        self.store = store
        self.name = name
        self.page = page

class User:
    """Represents a User/Member."""
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __eq__(self, other):
        return isinstance(other, User) and self.username == other.username

    def __hash__(self):
        return hash(self.username)

class DataStore:
    """In-memory data store for the application."""
    def __init__(self):
        self._boards = []
        self._users = []

    def get_boards(self):
        return self._boards

    def get_users(self):
        return self._users

    def add_user(self, user):
        # Prevent duplicate users based on username
        if user not in self._users:
            self._users.append(user)

    def add_board(self, board):
        self._boards.append(board)

    def remove_board(self, board):
        if board in self._boards:
            self._boards.remove(board)

# --- Main Application Layout ---

class TrelloApp(ft.UserControl):
    """Main application class for the Trello-like Flet app."""

    def __init__(self, page, store):
        super().__init__()
        self.page = page
        self.store = store
        self.user = None
        self.boards = self.store.get_boards()

        # Define containers for different views
        self.boards_content = ft.Row(
            controls=[],
            wrap=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            spacing=20,
        )
        
        # This container holds the content for the current view (boards, members, single board)
        self.view_container = ft.Container(
            content=self.boards_content, # Default to boards content
            padding=ft.padding.all(20),
            expand=True,
        )

        # Initialize AppLayout base class
        super().__init__()
        
        # Set AppLayout properties
        self.content = self.view_container
        self.tight = True
        self.expand = True
        self.vertical_alignment = ft.CrossAxisAlignment.START

        # App Bar setup
        self.login_profile_button = ft.PopupMenuItem(text="Log in", on_click=self.login)
        self.appbar_items = [
            self.login_profile_button,
            ft.PopupMenuItem(text="Members", on_click=lambda e: self.page.go("/members")),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings"),
        ]
        
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Text(
                "Trolli",
                font_family="Pacifico",
                size=32,
                text_align=ft.TextAlign.START,
            ),
            center_title=False,
            toolbar_height=75,
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )
        
        self.page.appbar = self.appbar
        self.page.on_route_change = self.route_change
        self.page.update()

    def initialize(self):
        """Sets up the initial view and route."""
        self.page.views.append(
            ft.View(
                "/",
                [self.appbar, self],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.BLUE_GREY_200,
            )
        )
        
        # Create an initial board for demonstration if no boards exist
        if len(self.boards) == 0:
            self.create_new_board("My First Project Board")
            
        # Check for stored user on startup (optional persistent login)
        stored_user = self.page.client_storage.get("current_user")
        if stored_user:
            self.user = stored_user
            self._update_appbar_for_logged_in_user()
            
        self.page.go("/boards")
        self.page.update()

    # --- Authentication Methods ---
    
    def _update_appbar_for_logged_in_user(self):
        """Helper to update the app bar items after login."""
        self.login_profile_button.text = f"{self.user}'s Profile"
        self.login_profile_button.on_click = lambda e: self.page.go("/members")
        
        logout_button = ft.PopupMenuItem(text="Log out", on_click=self.logout)
        
        # Rebuild appbar items
        self.appbar_items.clear()
        self.appbar_items.append(self.login_profile_button)
        self.appbar_items.append(ft.PopupMenuItem(text="Members", on_click=lambda e: self.page.go("/members")))
        self.appbar_items.append(ft.PopupMenuItem())
        self.appbar_items.append(ft.PopupMenuItem(text="Settings"))
        self.appbar_items.append(logout_button)
        
        self.page.update()


    def login(self, e):
        """Shows the login dialog."""
        def close_dlg(e):
            if user_name.value == "" or password.value == "":
                user_name.error_text = "Please provide username"
                password.error_text = "Please provide password"
                self.page.update()
                return
            
            user = User(user_name.value, password.value)
            self.store.add_user(user) # Adds user if not exists
            self.user = user_name.value
            self.page.client_storage.set("current_user", user_name.value)

            self.page.close(dialog)
            self._update_appbar_for_logged_in_user()
            self.page.go("/boards")

        user_name = ft.TextField(label="User name", autofocus=True)
        password = ft.TextField(label="Password", password=True, can_reveal_password=True)
        dialog = ft.AlertDialog(
            title=ft.Text("Please log in or sign up"),
            content=ft.Column(
                [
                    user_name,
                    password,
                    ft.ElevatedButton(text="Login / Sign Up", on_click=close_dlg, width=float('inf')),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Login dialog dismissed!"),
        )
        self.page.open(dialog)
        self.page.update()

    def logout(self, e):
        """Logs out the current user."""
        self.user = None
        self.page.client_storage.remove("current_user")
        
        # Reset appbar items to logged out state
        self.login_profile_button.text = "Log in"
        self.login_profile_button.on_click = self.login
        
        self.appbar_items.clear()
        self.appbar_items.append(self.login_profile_button)
        self.appbar_items.append(ft.PopupMenuItem(text="Members", on_click=lambda e: self.page.go("/members")))
        self.appbar_items.append(ft.PopupMenuItem())
        self.appbar_items.append(ft.PopupMenuItem(text="Settings"))
        
        self.page.go("/boards")
        self.page.update()

    # --- Board Management Methods ---

    def add_board(self, e):
        """Opens a dialog to create a new board."""
        def close_dlg(e):
            # Check if the button clicked was 'Create' or if Enter was pressed in the text field
            is_create_action = (hasattr(e.control, "text") and e.control.text == "Create") or (type(e.control) is ft.TextField and e.control.value != "")
            
            if is_create_action and dialog_text.value.strip() != "":
                self.create_new_board(dialog_text.value.strip())
            
            self.page.close(dialog)
            self.page.update()

        def textfield_change(e):
            create_button.disabled = dialog_text.value.strip() == ""
            self.page.update()

        dialog_text = ft.TextField(
            label="New Board Name", on_submit=close_dlg, on_change=textfield_change, autofocus=True
        )
        create_button = ft.ElevatedButton(
            text="Create", bgcolor=ft.Colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Name your new board"),
            content=ft.Column(
                [
                    dialog_text,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", on_click=lambda e: self.page.close(dialog)),
                            create_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.open(dialog)
        self.page.update()

    def create_new_board(self, board_name):
        """Creates a new board and updates the view."""
        new_board = Board(self, self.store, board_name, self.page)
        self.store.add_board(new_board)
        self.hydrate_all_boards_view()
        self.page.update()

    def delete_board(self, e):
        """Deletes a board and updates the view."""
        self.store.remove_board(e.control.data)
        self.set_all_boards_view()

    # --- View Rendering Methods ---

    def hydrate_all_boards_view(self):
        """Renders the board cards into the boards_content container."""
        self.boards_content.controls.clear()
        
        # 1. Create New Board Card
        new_board_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=40, color=ft.Colors.BLUE_GREY_400),
                        ft.Text("Create New Board", weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                width=280,
                height=150,
                padding=20,
                on_click=self.add_board,
                ink=True,
                border_radius=ft.border_radius.all(12),
                bgcolor=ft.Colors.WHITE60,
                border=ft.border.all(1, ft.Colors.BLUE_GREY_200)
            ),
            elevation=1,
            width=280,
        )
        self.boards_content.controls.append(new_board_card)


        # 2. Existing Board Cards
        for i, board in enumerate(self.store.get_boards()):
            board_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(board.name, size=18, weight=ft.FontWeight.BOLD, expand=True, color=ft.Colors.WHITE),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, 
                                        icon_color=ft.Colors.WHITE70,
                                        icon_size=20,
                                        data=board,
                                        on_click=self.delete_board
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text("Click to open", color=ft.Colors.WHITE70, italic=True),
                        ],
                        spacing=15
                    ),
                    padding=20,
                    width=280,
                    height=150,
                    on_click=lambda e, idx=i: self.page.go(f"/board/{idx}"),
                    ink=True,
                    border_radius=ft.border_radius.all(12),
                    bgcolor=ft.colors.BLUE_700
                ),
                elevation=4,
                width=280,
            )
            self.boards_content.controls.append(board_card)
        
        self.page.update()

    def set_all_boards_view(self):
        """Switches the main content to display all boards."""
        self.hydrate_all_boards_view()
        self.view_container.content = self.boards_content
        self.page.update()

    def set_board_view(self, board_id: int):
        """Switches the main content to display a specific board."""
        try:
            board = self.store.get_boards()[board_id]
        except IndexError:
            self.page.go("/boards")
            return
            
        # Simple placeholder for a board view, simulating Trello lists
        board_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Board: {board.name}", size=30, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Back to Boards", 
                            on_click=lambda e: self.page.go("/boards"),
                            icon=ft.icons.ARROW_BACK
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True
                ),
                ft.Text("This is your task management area. Lists are scrollable!", color=ft.Colors.BLACK54),
                ft.Row(
                    [
                        # To Do List
                        ft.Card(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("To Do", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Divider(),
                                    ft.Card(ft.Container(ft.Text("Task 1: Plan features"), padding=10), elevation=1, width=float('inf')),
                                    ft.Card(ft.Container(ft.Text("Task 2: Setup Flet app"), padding=10), elevation=1, width=float('inf')),
                                    ft.TextButton("Add a card...", icon=ft.icons.ADD),
                                ], scroll=ft.ScrollMode.ADAPTIVE, expand=True), 
                                padding=10, 
                                height=400
                            ), 
                            width=300, 
                            elevation=2
                        ),
                        # In Progress List
                        ft.Card(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("In Progress", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Divider(),
                                    ft.Card(ft.Container(ft.Text("Task 3: Implement route changes"), padding=10), elevation=1, width=float('inf')),
                                    ft.TextButton("Add a card...", icon=ft.icons.ADD),
                                ], scroll=ft.ScrollMode.ADAPTIVE, expand=True), 
                                padding=10, 
                                height=400
                            ), 
                            width=300, 
                            elevation=2
                        ),
                        # Done List
                        ft.Card(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Done", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Divider(),
                                    ft.Card(ft.Container(ft.Text("Task 0: Initial setup"), padding=10), elevation=1, width=float('inf'), bgcolor=ft.colors.GREEN_100),
                                    ft.TextButton("Add a card...", icon=ft.icons.ADD),
                                ], scroll=ft.ScrollMode.ADAPTIVE, expand=True), 
                                padding=10, 
                                height=400
                            ), 
                            width=300, 
                            elevation=2
                        ),
                    ],
                    wrap=True,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    spacing=20
                )
            ],
            expand=True
        )
        self.view_container.content = ft.Container(content=board_view, padding=ft.padding.all(20), expand=True)
        self.page.update()

    def set_members_view(self):
        """Switches the main content to display the registered members."""
        
        users_list = ft.Column(
            [
                ft.Text("Registered Users (Members)", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Current User: {self.user if self.user else 'Not logged in'}", color=ft.Colors.BLACK54),
                ft.Divider()
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )
        
        for user in self.store.get_users():
            users_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.PERSON),
                    title=ft.Text(user.username, weight=ft.FontWeight.MEDIUM),
                    subtitle=ft.Text("Trolli App Member"),
                    trailing=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, color=ft.colors.GREEN_600) if user.username == self.user else None
                )
            )

        if not self.store.get_users():
            users_list.controls.append(ft.Text("No users signed up yet. Try logging in to create the first user!"))

        self.view_container.content = ft.Container(content=users_list, padding=ft.padding.all(20), expand=True)
        self.page.update()
        
    # --- Routing ---

    def route_change(self, e):
        """Handles navigation based on the URL route."""
        troute = ft.TemplateRoute(self.page.route)
        
        if troute.match("/"):
            # Redirect root to boards view
            self.page.go("/boards") 
            return
            
        elif troute.match("/board/:id"):
            # Go to specific board view
            board_id = int(troute.id)
            if board_id >= 0 and board_id < len(self.store.get_boards()):
                self.set_board_view(board_id)
            else:
                self.page.go("/boards") # Redirect if ID is invalid
            return
            
        elif troute.match("/boards"):
            # Go to all boards view
            self.set_all_boards_view()
            return
            
        elif troute.match("/members"):
            # Go to members list view
            self.set_members_view()
            return
            
        # Optional: Handle 404/not found route
        else:
            self.page.go("/boards")


def main(page: ft.Page):
    """The entry point of the Flet application."""
    page.title = "Flet Trello Clone"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_200
    page.fonts = {"Pacifico": "https://fonts.gstatic.com/s/pacifico/v27/FwZa7-aU7_Uo_4M80k0H1zY.woff2"}
    
    # Initialize the data store and the application
    store = DataStore()
    app = TrelloApp(page, store)
    
    page.add(app)
    page.update()
    
    app.initialize()


if __name__ == "__main__":
    # Note: assets_dir is typically used for local fonts/images. Removed here as the font is remote.
    ft.app(target=main)
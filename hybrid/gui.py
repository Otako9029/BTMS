"""
BTMS - Banking Transaction Management System (GUI Edition)
Front-end & User Interface: Python tkinter (Old Language)
Business Logic Engine & Storage: Rust (New Language via FFI DLL)

A modern, polished desktop GUI banking application powered by a compiled Rust backend engine.
Includes a login system with credentials stored in users.json.
"""

import ctypes
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox


# ──────────────────────────────────────────────────────────────────────
# Rust Core DLL Loader
# ──────────────────────────────────────────────────────────────────────

def load_rust_core():
    """Locates and loads the compiled Rust btms_core.dll using ctypes."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_paths = [
        os.path.join(base_dir, "rust_core", "target", "release", "btms_core.dll"),
        os.path.join(base_dir, "rust_core", "target", "debug", "btms_core.dll"),
    ]

    dll_path = None
    for path in search_paths:
        if os.path.exists(path):
            dll_path = path
            break

    if dll_path is None:
        raise FileNotFoundError(
            "Could not find btms_core.dll.\n"
            "Please compile the Rust library first using:\n"
            "  cd hybrid/rust_core && cargo build --release"
        )

    lib = ctypes.CDLL(dll_path)

    # Configure function signatures
    lib.btms_init.argtypes = [ctypes.c_double]
    lib.btms_init.restype = None

    lib.btms_get_balance.argtypes = []
    lib.btms_get_balance.restype = ctypes.c_double

    lib.btms_deposit.argtypes = [ctypes.c_double]
    lib.btms_deposit.restype = ctypes.c_int32

    lib.btms_withdraw.argtypes = [ctypes.c_double]
    lib.btms_withdraw.restype = ctypes.c_int32

    lib.btms_get_history_count.argtypes = []
    lib.btms_get_history_count.restype = ctypes.c_int32

    lib.btms_get_transaction.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.btms_get_transaction.restype = ctypes.c_int32

    return lib


class RustBankEngine:
    """Wrapper class that delegates all banking logic to the Rust DLL."""

    def __init__(self, rust_lib, initial_balance=5000.0):
        self.lib = rust_lib
        self.lib.btms_init(initial_balance)

    def get_balance(self):
        return self.lib.btms_get_balance()

    def deposit(self, amount):
        return self.lib.btms_deposit(amount)

    def withdraw(self, amount):
        return self.lib.btms_withdraw(amount)

    def get_history(self):
        """Fetch all transaction records from Rust's Vec<Transaction>."""
        count = self.lib.btms_get_history_count()
        records = []
        buf_size = 64
        buf = ctypes.create_string_buffer(buf_size)
        out_amount = ctypes.c_double()
        out_balance = ctypes.c_double()

        for i in range(count):
            res = self.lib.btms_get_transaction(
                i, buf, buf_size,
                ctypes.byref(out_amount),
                ctypes.byref(out_balance),
            )
            if res == 0:
                records.append({
                    "type": buf.value.decode("utf-8"),
                    "amount": out_amount.value,
                    "balance_after": out_balance.value,
                })
        return records


# ──────────────────────────────────────────────────────────────────────
# User Authentication (reads users.json)
# ──────────────────────────────────────────────────────────────────────

def get_users_file_path():
    """Return the absolute path to users.json next to this script."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def load_users():
    """Load the user database from users.json."""
    path = get_users_file_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("users", [])


def authenticate(user_id, password):
    """Validate credentials against users.json.

    Returns the user dict on success, or None on failure.
    """
    users = load_users()
    for user in users:
        if user["id"] == user_id and user["password"] == password:
            return user
    return None


def update_user_balance(user_id, new_balance):
    """Persist the updated balance for a user back to users.json."""
    path = get_users_file_path()
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for user in data.get("users", []):
            if user["id"] == user_id:
                user["balance"] = round(new_balance, 2)
                break
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to update balance in users.json: {e}")


# ──────────────────────────────────────────────────────────────────────
# Color Palette & Design Tokens
# ──────────────────────────────────────────────────────────────────────

COLORS = {
    "bg_dark":       "#0f1117",
    "bg_card":       "#1a1d28",
    "bg_card_alt":   "#22263a",
    "bg_input":      "#2a2e42",
    "accent":        "#6c63ff",
    "accent_hover":  "#7b73ff",
    "accent_green":  "#00c896",
    "accent_red":    "#ff6b6b",
    "accent_orange": "#ffb347",
    "text_primary":  "#e8e8f0",
    "text_secondary":"#9a9ab0",
    "text_muted":    "#6b6b80",
    "border":        "#2e3348",
    "success_bg":    "#0d2818",
    "error_bg":      "#2d0f0f",
    "gold":          "#ffd700",
}

FONT_FAMILY = "Segoe UI"


# ──────────────────────────────────────────────────────────────────────
# Login Window
# ──────────────────────────────────────────────────────────────────────

class LoginWindow(tk.Tk):
    """Login screen that authenticates the user before opening the banking dashboard."""

    def __init__(self, rust_lib):
        super().__init__()
        self.rust_lib = rust_lib
        self.authenticated_user = None

        # Window setup
        self.title("BTMS — Login")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_dark"])

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # ── Top Branding ──────────────────────────────────────────────
        spacer = tk.Frame(self, bg=COLORS["bg_dark"], height=40)
        spacer.pack()

        tk.Label(
            self, text="🏦", font=(FONT_FAMILY, 42),
            bg=COLORS["bg_dark"], fg=COLORS["accent"],
        ).pack(pady=(0, 4))

        tk.Label(
            self, text="BTMS", font=(FONT_FAMILY, 28, "bold"),
            bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
        ).pack()

        tk.Label(
            self, text="Banking Transaction Management System",
            font=(FONT_FAMILY, 10), bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
        ).pack(pady=(2, 0))

        # Tech badges
        badge_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        badge_frame.pack(pady=(8, 0))
        for text, color in [("Python UI", COLORS["accent_green"]), ("Rust Engine", COLORS["accent_orange"])]:
            tk.Label(
                badge_frame, text=text, font=(FONT_FAMILY, 7, "bold"),
                bg=color, fg="#000000", padx=6, pady=1,
            ).pack(side=tk.LEFT, padx=3)

        # ── Login Card ────────────────────────────────────────────────
        card = tk.Frame(self, bg=COLORS["bg_card"], padx=36, pady=28)
        card.pack(fill=tk.X, padx=48, pady=(24, 0))

        tk.Label(
            card, text="Sign In", font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            card, text="Enter your credentials to access your account",
            font=(FONT_FAMILY, 9), bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor=tk.W, pady=(0, 18))

        # User ID field
        tk.Label(
            card, text="USER ID", font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
        ).pack(anchor=tk.W, pady=(0, 4))

        id_frame = tk.Frame(card, bg=COLORS["bg_input"], padx=10, pady=8)
        id_frame.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            id_frame, text="👤", font=(FONT_FAMILY, 12),
            bg=COLORS["bg_input"], fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT)

        self.id_entry = tk.Entry(
            id_frame, font=(FONT_FAMILY, 12), bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief=tk.FLAT, borderwidth=0,
        )
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        # Password field
        tk.Label(
            card, text="PASSWORD", font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
        ).pack(anchor=tk.W, pady=(0, 4))

        pw_frame = tk.Frame(card, bg=COLORS["bg_input"], padx=10, pady=8)
        pw_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            pw_frame, text="🔒", font=(FONT_FAMILY, 12),
            bg=COLORS["bg_input"], fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT)

        self.pw_entry = tk.Entry(
            pw_frame, font=(FONT_FAMILY, 12), bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief=tk.FLAT, borderwidth=0, show="●",
        )
        self.pw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        # Show / Hide password toggle
        self._pw_visible = False
        self.toggle_btn = tk.Label(
            pw_frame, text="👁", font=(FONT_FAMILY, 12),
            bg=COLORS["bg_input"], fg=COLORS["text_muted"], cursor="hand2",
        )
        self.toggle_btn.pack(side=tk.RIGHT)
        self.toggle_btn.bind("<Button-1>", self._toggle_password)

        # Error label
        self.error_label = tk.Label(
            card, text="", font=(FONT_FAMILY, 9),
            bg=COLORS["bg_card"], fg=COLORS["accent_red"],
        )
        self.error_label.pack(pady=(4, 8))

        # Sign In button
        self.login_btn = tk.Button(
            card, text="Sign In", font=(FONT_FAMILY, 12, "bold"),
            bg=COLORS["accent"], fg="#ffffff", activebackground=COLORS["accent_hover"],
            activeforeground="#ffffff", relief=tk.FLAT, cursor="hand2",
            padx=20, pady=10, command=self._on_login,
            borderwidth=0, highlightthickness=0,
        )
        self.login_btn.pack(fill=tk.X, pady=(0, 4))
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.configure(bg=COLORS["accent_hover"]))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.configure(bg=COLORS["accent"]))

        # Footer
        tk.Label(
            self, text="Secured by Rust Core Engine  •  btms_core.dll",
            font=(FONT_FAMILY, 8), bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
        ).pack(pady=(16, 0))

        # Key bindings
        self.bind("<Return>", lambda e: self._on_login())
        self.id_entry.focus_set()

    def _toggle_password(self, event=None):
        """Toggle password visibility."""
        self._pw_visible = not self._pw_visible
        self.pw_entry.config(show="" if self._pw_visible else "●")
        self.toggle_btn.config(text="🙈" if self._pw_visible else "👁")

    def _on_login(self):
        """Validate credentials and proceed if authenticated."""
        user_id = self.id_entry.get().strip()
        password = self.pw_entry.get().strip()

        if not user_id or not password:
            self.error_label.config(text="⚠  Please enter both User ID and Password.")
            return

        user = authenticate(user_id, password)
        if user is None:
            self.error_label.config(text="⚠  Invalid User ID or Password.")
            self.pw_entry.delete(0, tk.END)
            return

        # Authenticated — launch the banking dashboard
        self.authenticated_user = user
        self.destroy()


# ──────────────────────────────────────────────────────────────────────
# Main Banking Dashboard
# ──────────────────────────────────────────────────────────────────────

class BTMSApp(tk.Tk):
    """Main application class for the BTMS GUI banking dashboard."""

    def __init__(self, engine: RustBankEngine, user: dict):
        super().__init__()
        self.engine = engine
        self.user = user

        # Window setup
        self.title(f"BTMS — {user['name']} ({user['id']})")
        self.geometry("900x700")
        self.minsize(800, 620)
        self.configure(bg=COLORS["bg_dark"])
        self.resizable(True, True)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

        # Build the UI
        self._build_header()
        self._build_balance_card()
        self._build_action_buttons()
        self._build_history_panel()
        self._build_status_bar()

        # Initial state
        self._refresh_balance()
        self._refresh_history()

    # ── Header ────────────────────────────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_dark"], pady=12)
        header.pack(fill=tk.X, padx=24)

        title_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="🏦", font=(FONT_FAMILY, 22),
            bg=COLORS["bg_dark"], fg=COLORS["accent"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(
            title_frame, text="BTMS", font=(FONT_FAMILY, 22, "bold"),
            bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="Banking Transaction System",
            font=(FONT_FAMILY, 10), bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
        ).pack(side=tk.LEFT, padx=(12, 0), pady=(8, 0))

        # Right side: user info + badges + logout
        right_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        right_frame.pack(side=tk.RIGHT)

        # User greeting
        tk.Label(
            right_frame, text=f"👤 {self.user['name']}",
            font=(FONT_FAMILY, 9, "bold"), bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(
            right_frame, text=f"({self.user['id']})",
            font=(FONT_FAMILY, 8), bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT, padx=(0, 12))

        # Logout button
        logout_btn = tk.Button(
            right_frame, text="⏻ Logout", font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["accent_red"], fg="#ffffff",
            activebackground="#992222", activeforeground="#ffffff",
            relief=tk.FLAT, cursor="hand2", padx=8, pady=2,
            command=self._on_logout, borderwidth=0, highlightthickness=0,
        )
        logout_btn.pack(side=tk.LEFT, padx=(0, 8))
        logout_btn.bind("<Enter>", lambda e: logout_btn.configure(bg="#992222"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.configure(bg=COLORS["accent_red"]))

        # Tech badges
        for text, color in [("Python UI", COLORS["accent_green"]), ("Rust Engine", COLORS["accent_orange"])]:
            badge = tk.Label(
                right_frame, text=text, font=(FONT_FAMILY, 8, "bold"),
                bg=color, fg="#000000", padx=8, pady=2,
            )
            badge.pack(side=tk.LEFT, padx=2)

    # ── Balance Card ──────────────────────────────────────────────────

    def _build_balance_card(self):
        card = tk.Frame(self, bg=COLORS["bg_card"], padx=28, pady=20)
        card.pack(fill=tk.X, padx=24, pady=(4, 12))

        tk.Label(
            card, text="CURRENT BALANCE", font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        ).pack(anchor=tk.W)

        self.balance_label = tk.Label(
            card, text="₱0.00", font=(FONT_FAMILY, 36, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["gold"],
        )
        self.balance_label.pack(anchor=tk.W, pady=(4, 0))

        tk.Label(
            card,
            text=f"Powered by Rust Core Engine  •  Account: {self.user['id']}",
            font=(FONT_FAMILY, 8), bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor=tk.W, pady=(4, 0))

    # ── Action Buttons ────────────────────────────────────────────────

    def _build_action_buttons(self):
        actions_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        actions_frame.pack(fill=tk.X, padx=24, pady=(0, 12))

        buttons = [
            ("💰  Deposit", COLORS["accent_green"], "#006644", self._on_deposit),
            ("💸  Withdraw", COLORS["accent_red"], "#992222", self._on_withdraw),
            ("🔄  Refresh", COLORS["accent"], COLORS["accent_hover"], self._on_refresh),
        ]

        for i, (text, bg_color, hover_color, command) in enumerate(buttons):
            btn = tk.Button(
                actions_frame, text=text, font=(FONT_FAMILY, 11, "bold"),
                bg=bg_color, fg="#ffffff", activebackground=hover_color,
                activeforeground="#ffffff", relief=tk.FLAT, cursor="hand2",
                padx=20, pady=10, command=command,
                borderwidth=0, highlightthickness=0,
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0 if i == 0 else 6, 0))

            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.configure(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.configure(bg=c))

    # ── Transaction History Panel ─────────────────────────────────────

    def _build_history_panel(self):
        panel = tk.Frame(self, bg=COLORS["bg_card"])
        panel.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 8))

        # Header row
        header_frame = tk.Frame(panel, bg=COLORS["bg_card"], pady=10, padx=16)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame, text="📋  TRANSACTION HISTORY",
            font=(FONT_FAMILY, 10, "bold"), bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
        ).pack(side=tk.LEFT)

        self.history_count_label = tk.Label(
            header_frame, text="0 transactions",
            font=(FONT_FAMILY, 9), bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        )
        self.history_count_label.pack(side=tk.RIGHT)

        # Column headers
        col_header = tk.Frame(panel, bg=COLORS["border"], padx=16, pady=6)
        col_header.pack(fill=tk.X)

        headers = [("#", 40), ("Type", 120), ("Amount", 160), ("Balance After", 160)]
        for text, width in headers:
            tk.Label(
                col_header, text=text, font=(FONT_FAMILY, 8, "bold"),
                bg=COLORS["border"], fg=COLORS["text_muted"],
                width=width // 8, anchor=tk.W,
            ).pack(side=tk.LEFT, padx=(0, 8))

        # Scrollable history list
        list_container = tk.Frame(panel, bg=COLORS["bg_card"])
        list_container.pack(fill=tk.BOTH, expand=True)

        self.history_canvas = tk.Canvas(
            list_container, bg=COLORS["bg_card"],
            highlightthickness=0, borderwidth=0,
        )
        scrollbar = tk.Scrollbar(
            list_container, orient=tk.VERTICAL,
            command=self.history_canvas.yview,
        )
        self.history_inner = tk.Frame(self.history_canvas, bg=COLORS["bg_card"])

        self.history_inner.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self.history_canvas.create_window((0, 0), window=self.history_inner, anchor=tk.NW)
        self.history_canvas.configure(yscrollcommand=scrollbar.set)

        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        self.history_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.history_canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

    # ── Status Bar ────────────────────────────────────────────────────

    def _build_status_bar(self):
        status = tk.Frame(self, bg=COLORS["bg_card_alt"], pady=6)
        status.pack(fill=tk.X, padx=0, side=tk.BOTTOM)

        self.status_label = tk.Label(
            status,
            text=f"  ✅  Logged in as {self.user['name']}  •  Rust Core Engine connected",
            font=(FONT_FAMILY, 8),
            bg=COLORS["bg_card_alt"],
            fg=COLORS["accent_green"],
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, padx=12)

    # ── Event Handlers ────────────────────────────────────────────────

    def _on_deposit(self):
        """Show deposit dialog and process via Rust engine."""
        self._show_transaction_dialog("Deposit", COLORS["accent_green"])

    def _on_withdraw(self):
        """Show withdrawal dialog and process via Rust engine."""
        self._show_transaction_dialog("Withdraw", COLORS["accent_red"])

    def _on_refresh(self):
        """Refresh balance and transaction history from Rust core."""
        self._refresh_balance()
        self._refresh_history()
        self._set_status("🔄  Refreshed from Rust Core Engine", COLORS["accent"])

    def _on_logout(self):
        """Log out and return to the login screen."""
        self.destroy()
        run_app(self.engine.lib)  # Restart from login

    def _show_transaction_dialog(self, tx_type, accent_color):
        """Create a modal dialog window for deposit or withdrawal input."""
        dialog = tk.Toplevel(self)
        dialog.title(f"{tx_type} Money")
        dialog.geometry("400x260")
        dialog.resizable(False, False)
        dialog.configure(bg=COLORS["bg_dark"])
        dialog.transient(self)
        dialog.grab_set()

        # Center relative to main window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 130
        dialog.geometry(f"+{x}+{y}")

        # Dialog content
        tk.Label(
            dialog, text=f"{'💰' if tx_type == 'Deposit' else '💸'}  {tx_type} Money",
            font=(FONT_FAMILY, 16, "bold"), bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(pady=(20, 4))

        tk.Label(
            dialog, text=f"Enter amount to {tx_type.lower()}",
            font=(FONT_FAMILY, 9), bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
        ).pack(pady=(0, 16))

        # Amount input
        input_frame = tk.Frame(dialog, bg=COLORS["bg_input"], padx=12, pady=8)
        input_frame.pack(padx=40, fill=tk.X)

        tk.Label(
            input_frame, text="₱", font=(FONT_FAMILY, 18, "bold"),
            bg=COLORS["bg_input"], fg=COLORS["gold"],
        ).pack(side=tk.LEFT)

        amount_entry = tk.Entry(
            input_frame, font=(FONT_FAMILY, 18), bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief=tk.FLAT, borderwidth=0,
        )
        amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        amount_entry.focus_set()

        # Error message label (hidden initially)
        error_label = tk.Label(
            dialog, text="", font=(FONT_FAMILY, 9),
            bg=COLORS["bg_dark"], fg=COLORS["accent_red"],
        )
        error_label.pack(pady=(8, 0))

        def submit():
            text = amount_entry.get().strip()
            try:
                amount = float(text)
            except ValueError:
                error_label.config(text="⚠  Please enter a valid numeric amount.")
                return

            if tx_type == "Deposit":
                code = self.engine.deposit(amount)
                if code == -1:
                    error_label.config(text="⚠  Amount must be greater than zero.")
                    return
            else:
                code = self.engine.withdraw(amount)
                if code == -1:
                    error_label.config(text="⚠  Amount must be greater than zero.")
                    return
                if code == -2:
                    bal = self.engine.get_balance()
                    error_label.config(text=f"⚠  Insufficient funds. Balance: ₱{bal:,.2f}")
                    return

            dialog.destroy()
            new_bal = self.engine.get_balance()
            self.user["balance"] = new_bal
            update_user_balance(self.user["id"], new_bal)
            self._refresh_balance()
            self._refresh_history()
            self._set_status(
                f"{'💰' if tx_type == 'Deposit' else '💸'}  "
                f"{tx_type} of ₱{amount:,.2f} processed by Rust Engine",
                accent_color,
            )

        # Submit button
        btn = tk.Button(
            dialog, text=f"Confirm {tx_type}", font=(FONT_FAMILY, 11, "bold"),
            bg=accent_color, fg="#ffffff", activebackground=accent_color,
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=submit, borderwidth=0,
        )
        btn.pack(pady=(12, 0))

        # Enter key shortcut
        dialog.bind("<Return>", lambda e: submit())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    # ── UI Refresh Methods ────────────────────────────────────────────

    def _refresh_balance(self):
        """Update the balance display from the Rust core."""
        bal = self.engine.get_balance()
        self.balance_label.config(text=f"₱{bal:,.2f}")

    def _refresh_history(self):
        """Rebuild the transaction history list from Rust's Vec<Transaction>."""
        # Clear existing rows
        for widget in self.history_inner.winfo_children():
            widget.destroy()

        records = self.engine.get_history()
        self.history_count_label.config(text=f"{len(records)} transaction{'s' if len(records) != 1 else ''}")

        if not records:
            tk.Label(
                self.history_inner,
                text="\n\n  No transactions yet. Make a deposit or withdrawal to get started!",
                font=(FONT_FAMILY, 10), bg=COLORS["bg_card"],
                fg=COLORS["text_muted"], anchor=tk.W,
            ).pack(fill=tk.X, padx=16)
            return

        for i, rec in enumerate(records):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_card_alt"]
            row = tk.Frame(self.history_inner, bg=bg, padx=16, pady=8)
            row.pack(fill=tk.X)

            # Index
            tk.Label(
                row, text=str(i + 1), font=(FONT_FAMILY, 10),
                bg=bg, fg=COLORS["text_muted"], width=5, anchor=tk.W,
            ).pack(side=tk.LEFT)

            # Type with color indicator
            is_deposit = rec["type"] == "Deposit"
            type_color = COLORS["accent_green"] if is_deposit else COLORS["accent_red"]
            type_icon = "▲" if is_deposit else "▼"
            tk.Label(
                row, text=f"{type_icon}  {rec['type']}",
                font=(FONT_FAMILY, 10, "bold"), bg=bg,
                fg=type_color, width=15, anchor=tk.W,
            ).pack(side=tk.LEFT)

            # Amount
            sign = "+" if is_deposit else "−"
            tk.Label(
                row, text=f"{sign} ₱{rec['amount']:,.2f}",
                font=(FONT_FAMILY, 10), bg=bg,
                fg=type_color, width=18, anchor=tk.W,
            ).pack(side=tk.LEFT)

            # Balance after
            tk.Label(
                row, text=f"₱{rec['balance_after']:,.2f}",
                font=(FONT_FAMILY, 10, "bold"), bg=bg,
                fg=COLORS["text_primary"], width=18, anchor=tk.W,
            ).pack(side=tk.LEFT)

    def _set_status(self, text, color):
        """Update the status bar message."""
        self.status_label.config(text=f"  {text}", fg=color)


# ──────────────────────────────────────────────────────────────────────
# Application Flow
# ──────────────────────────────────────────────────────────────────────

def run_app(rust_lib):
    """Run the login → dashboard flow."""
    # Show login screen
    login = LoginWindow(rust_lib)
    login.mainloop()

    # Check if login was successful
    user = login.authenticated_user
    if user is None:
        return  # User closed the login window

    # Initialize Rust engine with the user's balance
    engine = RustBankEngine(rust_lib, initial_balance=user.get("balance", 5000.0))

    # Launch the banking dashboard
    app = BTMSApp(engine, user)
    app.mainloop()


def main():
    try:
        rust_lib = load_rust_core()
    except FileNotFoundError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("BTMS — Engine Not Found", str(e))
        root.destroy()
        return

    run_app(rust_lib)


if __name__ == "__main__":
    main()

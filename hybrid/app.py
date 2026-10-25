"""
BTMS - Banking Transaction Management System (Hybrid Edition)
Front-end & User Interface: Python (Old Language)
Business Logic Engine & Storage: Rust (New Language via FFI DLL)
"""

import ctypes
import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def load_rust_core():
    """Locates and loads the compiled Rust btms_core.dll using ctypes."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dll_path = os.path.join(base_dir, "rust_core", "target", "release", "btms_core.dll")

    if not os.path.exists(dll_path):
        # Fallback to current directory or debug build
        dll_path = os.path.join(base_dir, "rust_core", "target", "debug", "btms_core.dll")

    if not os.path.exists(dll_path):
        raise FileNotFoundError(
            f"Could not find btms_core.dll at:\n{dll_path}\n"
            "Please compile the Rust library first using:\n"
            "  cd hybrid/rust_core && cargo build --release"
        )

    lib = ctypes.CDLL(dll_path)

    # Function signatures configuration (C ABI types)
    # btms_init(f64)
    lib.btms_init.argtypes = [ctypes.c_double]
    lib.btms_init.restype = None

    # btms_get_balance() -> f64
    lib.btms_get_balance.argtypes = []
    lib.btms_get_balance.restype = ctypes.c_double

    # btms_deposit(f64) -> i32
    lib.btms_deposit.argtypes = [ctypes.c_double]
    lib.btms_deposit.restype = ctypes.c_int32

    # btms_withdraw(f64) -> i32
    lib.btms_withdraw.argtypes = [ctypes.c_double]
    lib.btms_withdraw.restype = ctypes.c_int32

    # btms_get_history_count() -> i32
    lib.btms_get_history_count.argtypes = []
    lib.btms_get_history_count.restype = ctypes.c_int32

    # btms_get_transaction(i32, *mut u8, usize, *mut f64, *mut f64) -> i32
    lib.btms_get_transaction.argtypes = [
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.btms_get_transaction.restype = ctypes.c_int32

    return lib


class HybridBankAccount:
    """Python wrapper class that delegates all banking logic to the Rust core engine."""

    def __init__(self, rust_lib, initial_balance=5000.0):
        self.lib = rust_lib
        self.lib.btms_init(initial_balance)

    def get_balance(self):
        """Retrieve current balance directly from Rust memory."""
        return self.lib.btms_get_balance()

    def deposit(self, amount):
        """Invoke Rust deposit handler with validation."""
        code = self.lib.btms_deposit(amount)
        if code == -1:
            print("\n  [ERROR] Deposit amount must be greater than zero.")
            return False
        
        balance = self.get_balance()
        print(f"\n  [Rust Engine] Successfully deposited ₱{amount:,.2f}")
        print(f"  [Rust Engine] Updated Balance: ₱{balance:,.2f}")
        return True

    def withdraw(self, amount):
        """Invoke Rust withdrawal handler with safety checks."""
        code = self.lib.btms_withdraw(amount)
        if code == -1:
            print("\n  [ERROR] Withdrawal amount must be greater than zero.")
            return False
        if code == -2:
            balance = self.get_balance()
            print(f"\n  [ERROR] Insufficient funds. Available balance: ₱{balance:,.2f}")
            return False

        balance = self.get_balance()
        print(f"\n  [Rust Engine] Successfully withdrew ₱{amount:,.2f}")
        print(f"  [Rust Engine] Updated Balance: ₱{balance:,.2f}")
        return True

    def view_history(self):
        """Fetch transaction history records stored in Rust's Vec<Transaction>."""
        count = self.lib.btms_get_history_count()
        if count == 0:
            print("\n  No transactions recorded yet in Rust core.")
            return

        print("\n  ╔══════╦══════════════╦═══════════════╦═══════════════════╗")
        print("  ║  #   ║ Type         ║ Amount        ║ Balance After     ║")
        print("  ╠══════╬══════════════╬═══════════════╬═══════════════════╣")

        buf_size = 64
        buf = ctypes.create_string_buffer(buf_size)
        out_amount = ctypes.c_double()
        out_balance = ctypes.c_double()

        for i in range(count):
            res = self.lib.btms_get_transaction(
                i,
                buf,
                buf_size,
                ctypes.byref(out_amount),
                ctypes.byref(out_balance),
            )
            if res == 0:
                t_type = buf.value.decode("utf-8")
                t_amt = f"₱{out_amount.value:,.2f}"
                t_bal = f"₱{out_balance.value:,.2f}"
                print(f"  ║ {i + 1:<4} ║ {t_type:<12} ║ {t_amt:>13} ║ {t_bal:>17} ║")

        print("  ╚══════╩══════════════╩═══════════════╩═══════════════════╝")


def read_amount(prompt):
    """Input validation in Python layer for numeric entries."""
    while True:
        try:
            val = float(input(prompt))
            return val
        except ValueError:
            print("  [ERROR] Invalid input. Please enter a numeric amount.")


def main():
    try:
        rust_lib = load_rust_core()
    except Exception as e:
        print(f"[FATAL] Failed to load Rust engine: {e}")
        return

    account = HybridBankAccount(rust_lib, initial_balance=5000.0)

    banner = r"""
  ╔═══════════════════════════════════════════════════╗
  ║         BTMS - Banking Transaction System         ║
  ║               HYBRID ARCHITECTURE                 ║
  ║      Python (Frontend UI) + Rust (Core Engine)    ║
  ╚═══════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"  Account initialized via Rust Core. Balance: ₱{account.get_balance():,.2f}\n")

    while True:
        print("  ┌─────────────── MENU ───────────────┐")
        print("  │  [1]  Check Balance                 │")
        print("  │  [2]  Deposit Money                 │")
        print("  │  [3]  Withdraw Money                │")
        print("  │  [4]  View Transaction History      │")
        print("  │  [5]  Exit                          │")
        print("  └─────────────────────────────────────┘")

        choice = input("  Enter your choice (1-5): ").strip()

        if choice == "1":
            print(f"\n  Current Balance: ₱{account.get_balance():,.2f}\n")
        elif choice == "2":
            amount = read_amount("  Enter deposit amount: ₱")
            account.deposit(amount)
            print()
        elif choice == "3":
            amount = read_amount("  Enter withdrawal amount: ₱")
            account.withdraw(amount)
            print()
        elif choice == "4":
            account.view_history()
            print()
        elif choice == "5":
            print("\n  Thank you for using BTMS Hybrid! Goodbye!\n")
            break
        else:
            print("\n  [ERROR] Invalid choice. Please select 1-5.\n")


if __name__ == "__main__":
    main()

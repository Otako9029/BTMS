"""
BTMS - Banking Transaction Management System
A simple menu-driven banking application prototype.
Language: Python (Old Language)
"""


class BankAccount:
    """Represents a bank account with balance tracking and transaction history."""

    def __init__(self, initial_balance=5000.0):
        """Initialize account with a starting balance and empty transaction history.

        Args:
            initial_balance: Starting balance in PHP (default: 5000.0)
        """
        self.balance = initial_balance
        self.history = []  # list of dicts: {"type", "amount", "balance_after"}

    def deposit(self, amount):
        """Process a deposit transaction.

        Validates that the amount is positive, updates the balance,
        and records the transaction in history.

        Args:
            amount: The amount to deposit (must be > 0)

        Returns:
            True if deposit was successful, False otherwise.
        """
        if amount <= 0:
            print("\n  [ERROR] Deposit amount must be greater than zero.")
            return False

        self.balance += amount
        self.history.append({
            "type": "Deposit",
            "amount": amount,
            "balance_after": self.balance,
        })
        print(f"\n  Successfully deposited ₱{amount:,.2f}")
        print(f"  Updated Balance: ₱{self.balance:,.2f}")
        return True

    def withdraw(self, amount):
        """Process a withdrawal transaction.

        Validates that the amount is positive and does not exceed
        the available balance, then updates the balance and records
        the transaction in history.

        Args:
            amount: The amount to withdraw (must be > 0 and <= balance)

        Returns:
            True if withdrawal was successful, False otherwise.
        """
        if amount <= 0:
            print("\n  [ERROR] Withdrawal amount must be greater than zero.")
            return False

        if amount > self.balance:
            print(f"\n  [ERROR] Insufficient funds. Available balance: ₱{self.balance:,.2f}")
            return False

        self.balance -= amount
        self.history.append({
            "type": "Withdrawal",
            "amount": amount,
            "balance_after": self.balance,
        })
        print(f"\n  Successfully withdrew ₱{amount:,.2f}")
        print(f"  Updated Balance: ₱{self.balance:,.2f}")
        return True

    def view_history(self):
        """Display all recorded transactions in a formatted table."""
        if not self.history:
            print("\n  No transactions recorded yet.")
            return

        print("\n  ╔══════╦══════════════╦═══════════════╦═══════════════════╗")
        print("  ║  #   ║ Type         ║ Amount        ║ Balance After     ║")
        print("  ╠══════╬══════════════╬═══════════════╬═══════════════════╣")
        for i, txn in enumerate(self.history, start=1):
            t_type = txn["type"]
            t_amt = f"₱{txn['amount']:,.2f}"
            t_bal = f"₱{txn['balance_after']:,.2f}"
            print(f"  ║ {i:<4} ║ {t_type:<12} ║ {t_amt:>13} ║ {t_bal:>17} ║")
        print("  ╚══════╩══════════════╩═══════════════╩═══════════════════╝")


def read_amount(prompt):
    """Prompt the user to enter a monetary amount with input validation.

    Repeatedly asks until a valid numeric value is entered.

    Args:
        prompt: The message to display to the user.

    Returns:
        A float value entered by the user.
    """
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("  [ERROR] Invalid input. Please enter a numeric amount.")


def main():
    """Run the main banking menu loop."""
    account = BankAccount(initial_balance=5000.0)

    banner = r"""
  ╔═══════════════════════════════════════════════╗
  ║       BTMS - Banking Transaction System       ║
  ║              Python  Implementation           ║
  ╚═══════════════════════════════════════════════╝
    """
    print(banner)
    print(f"  Account initialized with balance: ₱{account.balance:,.2f}\n")

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
            print(f"\n  Current Balance: ₱{account.balance:,.2f}\n")

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
            print("\n  Thank you for using BTMS. Goodbye!\n")
            break

        else:
            print("\n  [ERROR] Invalid choice. Please select 1-5.\n")


if __name__ == "__main__":
    main()

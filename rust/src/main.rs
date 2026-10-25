/// BTMS — Banking Transaction Management System
/// A simple menu-driven banking application prototype.
/// Language: Rust (New Language)

use std::io::{self, Write};

/// Represents a single recorded transaction.
struct Transaction {
    tx_type: String,     // "Deposit" or "Withdrawal"
    amount: f64,         // transaction amount
    balance_after: f64,  // account balance after the transaction
}

/// Represents a bank account with balance tracking and transaction history.
struct BankAccount {
    balance: f64,
    history: Vec<Transaction>,
}

impl BankAccount {
    /// Create a new account with the given starting balance.
    fn new(initial_balance: f64) -> Self {
        BankAccount {
            balance: initial_balance,
            history: Vec::new(),
        }
    }

    /// Process a deposit transaction.
    ///
    /// Validates that the amount is positive, updates the balance,
    /// and records the transaction in history.
    ///
    /// Returns `true` if the deposit was successful.
    fn deposit(&mut self, amount: f64) -> bool {
        if amount <= 0.0 {
            println!("\n  [ERROR] Deposit amount must be greater than zero.");
            return false;
        }

        self.balance += amount;
        self.history.push(Transaction {
            tx_type: String::from("Deposit"),
            amount,
            balance_after: self.balance,
        });
        println!("\n  Successfully deposited ₱{:.2}", amount);
        println!("  Updated Balance: ₱{:.2}", self.balance);
        true
    }

    /// Process a withdrawal transaction.
    ///
    /// Validates that the amount is positive and does not exceed the available
    /// balance, then updates the balance and records the transaction in history.
    ///
    /// Returns `true` if the withdrawal was successful.
    fn withdraw(&mut self, amount: f64) -> bool {
        if amount <= 0.0 {
            println!("\n  [ERROR] Withdrawal amount must be greater than zero.");
            return false;
        }

        if amount > self.balance {
            println!(
                "\n  [ERROR] Insufficient funds. Available balance: ₱{:.2}",
                self.balance
            );
            return false;
        }

        self.balance -= amount;
        self.history.push(Transaction {
            tx_type: String::from("Withdrawal"),
            amount,
            balance_after: self.balance,
        });
        println!("\n  Successfully withdrew ₱{:.2}", amount);
        println!("  Updated Balance: ₱{:.2}", self.balance);
        true
    }

    /// Display all recorded transactions in a formatted table.
    fn view_history(&self) {
        if self.history.is_empty() {
            println!("\n  No transactions recorded yet.");
            return;
        }

        println!();
        println!("  ╔══════╦══════════════╦═══════════════╦═══════════════════╗");
        println!("  ║  #   ║ Type         ║ Amount        ║ Balance After     ║");
        println!("  ╠══════╬══════════════╬═══════════════╬═══════════════════╣");
        for (i, txn) in self.history.iter().enumerate() {
            println!(
                "  ║ {:<4} ║ {:<12} ║ {:>13} ║ {:>17} ║",
                i + 1,
                txn.tx_type,
                format!("₱{:.2}", txn.amount),
                format!("₱{:.2}", txn.balance_after),
            );
        }
        println!("  ╚══════╩══════════════╩═══════════════╩═══════════════════╝");
    }
}

/// Prompt the user to enter a monetary amount with input validation.
///
/// Repeatedly asks until a valid numeric value is entered.
fn read_amount(prompt: &str) -> f64 {
    loop {
        print!("{}", prompt);
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).expect("Failed to read input");

        match input.trim().parse::<f64>() {
            Ok(value) => return value,
            Err(_) => println!("  [ERROR] Invalid input. Please enter a numeric amount."),
        }
    }
}

/// Read a single line from stdin, trimmed.
fn read_line() -> String {
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Failed to read input");
    input.trim().to_string()
}

/// Run the main banking menu loop.
fn main() {
    let mut account = BankAccount::new(5000.0);

    println!();
    println!("  ╔═══════════════════════════════════════════════╗");
    println!("  ║       BTMS - Banking Transaction System       ║");
    println!("  ║               Rust  Implementation            ║");
    println!("  ╚═══════════════════════════════════════════════╝");
    println!();
    println!("  Account initialized with balance: ₱{:.2}\n", account.balance);

    loop {
        println!("  ┌─────────────── MENU ───────────────┐");
        println!("  │  [1]  Check Balance                 │");
        println!("  │  [2]  Deposit Money                 │");
        println!("  │  [3]  Withdraw Money                │");
        println!("  │  [4]  View Transaction History      │");
        println!("  │  [5]  Exit                          │");
        println!("  └─────────────────────────────────────┘");

        print!("  Enter your choice (1-5): ");
        io::stdout().flush().unwrap();

        let choice = read_line();

        match choice.as_str() {
            "1" => {
                println!("\n  Current Balance: ₱{:.2}\n", account.balance);
            }
            "2" => {
                let amount = read_amount("  Enter deposit amount: ₱");
                account.deposit(amount);
                println!();
            }
            "3" => {
                let amount = read_amount("  Enter withdrawal amount: ₱");
                account.withdraw(amount);
                println!();
            }
            "4" => {
                account.view_history();
                println!();
            }
            "5" => {
                println!("\n  Thank you for using BTMS. Goodbye!\n");
                break;
            }
            _ => {
                println!("\n  [ERROR] Invalid choice. Please select 1-5.\n");
            }
        }
    }
}

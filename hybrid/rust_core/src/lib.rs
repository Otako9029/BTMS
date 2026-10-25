/// BTMS Core - Rust Backend Engine
/// Compiled into a dynamic library (DLL) exposing C-ABI functions for Python via FFI / ctypes.

use std::sync::Mutex;

/// Represents a single recorded transaction.
#[derive(Clone)]
pub struct Transaction {
    pub tx_type: String,     // "Deposit" or "Withdrawal"
    pub amount: f64,
    pub balance_after: f64,
}

/// Represents the bank account state managed by the Rust core.
pub struct BankAccount {
    pub balance: f64,
    pub history: Vec<Transaction>,
}

impl BankAccount {
    pub fn new(initial_balance: f64) -> Self {
        BankAccount {
            balance: initial_balance,
            history: Vec::new(),
        }
    }

    pub fn deposit(&mut self, amount: f64) -> i32 {
        if amount <= 0.0 {
            return -1; // Error: Invalid amount
        }
        self.balance += amount;
        self.history.push(Transaction {
            tx_type: String::from("Deposit"),
            amount,
            balance_after: self.balance,
        });
        0 // Success
    }

    pub fn withdraw(&mut self, amount: f64) -> i32 {
        if amount <= 0.0 {
            return -1; // Error: Invalid amount
        }
        if amount > self.balance {
            return -2; // Error: Insufficient funds
        }
        self.balance -= amount;
        self.history.push(Transaction {
            tx_type: String::from("Withdrawal"),
            amount,
            balance_after: self.balance,
        });
        0 // Success
    }
}

// Global thread-safe singleton instance for the C interface
static ACCOUNT: Mutex<Option<BankAccount>> = Mutex::new(None);

#[no_mangle]
pub extern "C" fn btms_init(initial_balance: f64) {
    let mut lock = ACCOUNT.lock().unwrap();
    *lock = Some(BankAccount::new(initial_balance));
}

#[no_mangle]
pub extern "C" fn btms_get_balance() -> f64 {
    let lock = ACCOUNT.lock().unwrap();
    match lock.as_ref() {
        Some(acc) => acc.balance,
        None => 0.0,
    }
}

#[no_mangle]
pub extern "C" fn btms_deposit(amount: f64) -> i32 {
    let mut lock = ACCOUNT.lock().unwrap();
    match lock.as_mut() {
        Some(acc) => acc.deposit(amount),
        None => -3, // Not initialized
    }
}

#[no_mangle]
pub extern "C" fn btms_withdraw(amount: f64) -> i32 {
    let mut lock = ACCOUNT.lock().unwrap();
    match lock.as_mut() {
        Some(acc) => acc.withdraw(amount),
        None => -3, // Not initialized
    }
}

#[no_mangle]
pub extern "C" fn btms_get_history_count() -> i32 {
    let lock = ACCOUNT.lock().unwrap();
    match lock.as_ref() {
        Some(acc) => acc.history.len() as i32,
        None => 0,
    }
}

/// Retrieve a specific transaction record by zero-based index.
/// Writes the transaction type into out_type_buf (as null-terminated UTF-8),
/// and outputs amount and balance_after through pointer parameters.
/// Returns 0 on success, or -1 if index is out of bounds.
#[no_mangle]
pub unsafe extern "C" fn btms_get_transaction(
    index: i32,
    out_type_buf: *mut u8,
    buf_size: usize,
    out_amount: *mut f64,
    out_balance_after: *mut f64,
) -> i32 {
    if index < 0 || out_type_buf.is_null() || out_amount.is_null() || out_balance_after.is_null() {
        return -1;
    }

    let lock = ACCOUNT.lock().unwrap();
    let acc = match lock.as_ref() {
        Some(a) => a,
        None => return -1,
    };

    let idx = index as usize;
    if idx >= acc.history.len() {
        return -1;
    }

    let txn = &acc.history[idx];
    *out_amount = txn.amount;
    *out_balance_after = txn.balance_after;

    let bytes = txn.tx_type.as_bytes();
    let copy_len = bytes.len().min(buf_size.saturating_sub(1));
    std::ptr::copy_nonoverlapping(bytes.as_ptr(), out_type_buf, copy_len);
    *out_type_buf.add(copy_len) = 0; // Null terminator

    0
}

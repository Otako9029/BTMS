# BTMS — Test Cases

All test cases apply identically to both the **Python** and **Rust** implementations.
Starting balance for each test run: **₱5,000.00**.

---

## Test Case 1 — Check Initial Balance (Valid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run program | Banner displays, balance shown as ₱5,000.00 |
| 2 | Select option `1` | Displays "Current Balance: ₱5,000.00" |

**Status:** ✅ Pass

---

## Test Case 2 — Successful Deposit (Valid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select option `2` | Prompts for deposit amount |
| 2 | Enter `1500` | "Successfully deposited ₱1,500.00" |
| 3 | — | "Updated Balance: ₱6,500.00" |
| 4 | Select option `1` | Displays "Current Balance: ₱6,500.00" |

**Status:** ✅ Pass

---

## Test Case 3 — Successful Withdrawal (Valid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | (continue from TC2, balance = ₱6,500.00) | — |
| 2 | Select option `3` | Prompts for withdrawal amount |
| 3 | Enter `2000` | "Successfully withdrew ₱2,000.00" |
| 4 | — | "Updated Balance: ₱4,500.00" |

**Status:** ✅ Pass

---

## Test Case 4 — Withdrawal Exceeds Balance (Invalid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | (continue from TC3, balance = ₱4,500.00) | — |
| 2 | Select option `3` | Prompts for withdrawal amount |
| 3 | Enter `10000` | "[ERROR] Insufficient funds. Available balance: ₱4,500.00" |
| 4 | Select option `1` | Balance remains ₱4,500.00 (unchanged) |

**Status:** ✅ Pass

---

## Test Case 5 — Negative Deposit Amount (Invalid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select option `2` | Prompts for deposit amount |
| 2 | Enter `-500` | "[ERROR] Deposit amount must be greater than zero." |
| 3 | Select option `1` | Balance unchanged |

**Status:** ✅ Pass

---

## Test Case 6 — Invalid Menu Selection (Invalid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter `9` at menu | "[ERROR] Invalid choice. Please select 1-5." |
| 2 | Enter `abc` at menu | "[ERROR] Invalid choice. Please select 1-5." |
| 3 | Menu re-displays | User can make a valid selection |

**Status:** ✅ Pass

---

## Test Case 7 — Transaction History After Mixed Operations (Valid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Fresh run, select `2`, enter `1500` | Deposit recorded |
| 2 | Select `3`, enter `2000` | Withdrawal recorded |
| 3 | Select `2`, enter `750` | Deposit recorded |
| 4 | Select `4` | History table shows: |

**Expected History Output:**

```
  ╔══════╦══════════════╦═══════════════╦═══════════════════╗
  ║  #   ║ Type         ║ Amount        ║ Balance After     ║
  ╠══════╬══════════════╬═══════════════╬═══════════════════╣
  ║ 1    ║ Deposit      ║    ₱1,500.00  ║        ₱6,500.00  ║
  ║ 2    ║ Withdrawal   ║    ₱2,000.00  ║        ₱4,500.00  ║
  ║ 3    ║ Deposit      ║      ₱750.00  ║        ₱5,250.00  ║
  ╚══════╩══════════════╩═══════════════╩═══════════════════╝
```

**Status:** ✅ Pass

---

## Test Case 8 — User Authentication / Login (Valid & Invalid)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Launch GUI `python hybrid/gui.py` | Login screen appears with ID & Password fields |
| 2 | Leave fields empty and click **Sign In** | Error message: "⚠ Please enter both User ID and Password." |
| 3 | Enter wrong password (e.g. `wrongpass`) | Error message: "⚠ Invalid User ID or Password." |
| 4 | Enter valid ID `24-0637-187` & Password `24-0637-187` | Authentication succeeds, Dashboard opens |
| 5 | Verify header & greeting | Displays "👤 Test User (24-0637-187)" |

**Status:** ✅ Pass

---

## Test Case 9 — Balance Persistence Across Sessions

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in as `24-0637-187` | Initial balance loaded from `users.json` |
| 2 | Perform Deposit of `₱1,000.00` | Rust core processes deposit, new balance saved to `users.json` |
| 3 | Click **Logout** or close application | Session closes |
| 4 | Log in again as `24-0637-187` | Dashboard shows updated balance preserved from previous session |

**Status:** ✅ Pass

import os
from datetime import datetime
import getpass

ACCOUNTS_FILE = 'accounts.txt'
TRANSACTIONS_FILE = 'transactions.txt'
FD_FILE = 'fixed_deposits.txt'
SIP_FILE = 'sip_investments.txt'

def create_account():
    initial_deposit = float(input("Enter your initial deposit: "))

    if initial_deposit >= 20000:
        account_number = input("Enter your desired account number: ")
    else:
        print("You must deposit at least 20,000 INR to choose your own account number.")
        account_number = generate_account_number()  # Generate a default account number

    name = input("Enter your name: ")
    password = getpass.getpass("Enter a password: ")  # Masked password input
    balance = initial_deposit

    with open(ACCOUNTS_FILE, 'a') as f:
        f.write(f"{account_number},{name},{password},{balance}\n")

    print(f"Your account number: {account_number} (Save this for login)")
    print("Account created successfully! (Account details saved to accounts.txt)")

def generate_account_number():
    if not os.path.exists(ACCOUNTS_FILE):
        return "123456"  # Starting account number
    with open(ACCOUNTS_FILE, 'r') as f:
        lines = f.readlines()
        last_account_number = int(lines[-1].split(',')[0])
        return str(last_account_number + 1)

def login():
    account_number = input("Enter your account number: ")
    password = getpass.getpass("Enter your password: ")  # Masked password input

    with open(ACCOUNTS_FILE, 'r') as f:
        for line in f:
            acc_num, name, pwd, balance = line.strip().split(',')
            if acc_num == account_number and pwd == password:
                print("Login successful!")
                fd_balance = get_fd_balance(account_number)
                sip_balance = get_sip_balance(account_number)
                print(f"Your Savings Balance: {balance}")
                print(f"Your Fixed Deposit Balance: {fd_balance}")
                print(f"Your SIP Investment Balance: {sip_balance}")
                return account_number, float(balance)

    print("Invalid account number or password.")
    return None, None

def get_fd_balance(account_number):
    total_fd = 0.0
    if os.path.exists(FD_FILE):
        with open(FD_FILE, 'r') as f:
            for line in f:
                acc_num, amount, duration, date, interest = line.strip().split(',')
                if acc_num == account_number:
                    total_fd += float(amount)
    return total_fd

def get_sip_balance(account_number):
    total_sip = 0.0
    if os.path.exists(SIP_FILE):
        with open(SIP_FILE, 'r') as f:
            for line in f:
                acc_num, amount, months, date, interest = line.strip().split(',')
                if acc_num == account_number:
                    total_sip += float(amount)
    return total_sip

def deposit(account_number, balance):
    amount = float(input("Enter amount to deposit: "))
    balance += amount
    log_transaction(account_number, "Deposit", amount)
    print(f"Deposit successful! Current balance: {balance}")
    return balance

def withdraw(account_number, balance):
    amount = float(input("Enter amount to withdraw: "))
    if amount > balance:
        print("Insufficient balance!")
    else:
        balance -= amount
        log_transaction(account_number, "Withdrawal", amount)
        print(f"Withdrawal successful! Current balance: {balance}")
    return balance

def log_transaction(account_number, transaction_type, amount):
    date = datetime.now().strftime("%Y-%m-%d")
    with open(TRANSACTIONS_FILE, 'a') as f:
        f.write(f"{account_number},{transaction_type},{amount},{date}\n")

def forget_password():
    account_number = input("Enter your account number: ")
    name = input("Enter your registered name: ")

    found = False
    with open(ACCOUNTS_FILE, 'r') as f:
        lines = f.readlines()

    with open(ACCOUNTS_FILE, 'w') as f:
        for line in lines:
            acc_num, acc_name, pwd, balance = line.strip().split(',')
            if acc_num == account_number and acc_name == name:
                found = True
                print("Account verified!")
                new_password = getpass.getpass("Enter your new password: ")
                f.write(f"{acc_num},{acc_name},{new_password},{balance}\n")
                print("Password reset successfully!")
            else:
                f.write(line)

    if not found:
        print("Account verification failed. Please check your details.")

def open_fixed_deposit(account_number, balance):
    # Display available interest rates to the customer
    print("\nAvailable Fixed Deposit Interest Rates:")
    print("1. 6 to 12 months: 4% interest")
    print("2. 12 to 15 months: 7% interest")
    print("3. Above 15 months: 8% interest")

    # Get the duration of the FD
    duration = int(input("\nEnter the duration of the fixed deposit (in months): "))

    # Determine the interest rate based on the duration
    if 6 <= duration < 12:
        interest_rate = 4  # 4% interest rate for 6-12 months
    elif 12 <= duration <= 15:
        interest_rate = 7  # 7% interest rate for 12-15 months
    elif duration > 15:
        interest_rate = 8  # 8% interest rate for more than 15 months
    else:
        print("The minimum duration for a fixed deposit is 6 months.")
        return balance

    # Show interest rate before confirming the FD
    print(f"\nThe interest rate for a {duration}-month FD is {interest_rate}%.")

    # Ask if the customer wants to proceed with the FD booking
    confirm = input(f"Do you want to proceed with the {duration}-month FD at {interest_rate}% interest? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("FD booking cancelled.")
        return balance

    # Get the amount to be deposited for the FD
    amount = float(input("Enter the amount for fixed deposit: "))

    if amount > balance:
        print("Insufficient balance to open fixed deposit.")
        return balance

    # Calculate interest on the amount
    interest = (amount * interest_rate) / 100
    balance -= amount
    log_transaction(account_number, "Fixed Deposit Opened", amount)

    # Store FD details including interest earned
    with open(FD_FILE, 'a') as f:
        f.write(f"{account_number},{amount},{duration},{interest},{datetime.now().strftime('%Y-%m-%d')}\n")

    # Display the FD details to the customer
    print(f"\nFixed Deposit of {amount} RUS opened for {duration} months at an interest rate of {interest_rate}%.")
    print(f"Interest earned: {interest} RUS")
    print(f"Remaining balance after FD: {balance}")

    return balance

def open_sip(account_number, balance):
    # Display SIP details to the customer
    print("\nAvailable SIP Options:")
    print("1. SIP with 6% annual return")

    # Get the SIP amount and duration
    sip_amount = float(input("Enter the monthly SIP amount: "))
    sip_duration = int(input("Enter the duration of the SIP (in months): "))

    # Calculate interest on SIP (Fixed 6% annual return for simplicity)
    annual_return_rate = 6  # 6% annual return
    monthly_return_rate = annual_return_rate / 12 / 100  # Convert annual return to monthly

    # Check if the customer has enough balance to invest in SIP
    if sip_amount > balance:
        print("Insufficient balance to start SIP.")
        return balance

    balance -= sip_amount
    total_investment = sip_amount * sip_duration
    total_return = total_investment * (monthly_return_rate * sip_duration)

    # Log SIP investment
    log_transaction(account_number, "SIP Investment", total_investment)

    # Store SIP investment details
    with open(SIP_FILE, 'a') as f:
        f.write(f"{account_number},{sip_amount},{sip_duration},{datetime.now().strftime('%Y-%m-%d')},{total_return}\n")

    print(f"SIP investment of {sip_amount} RUS per month for {sip_duration} months has been successful!")
    print(f"Total SIP investment: {total_investment} RUS, Total return: {total_return} RUS.")
    print(f"Remaining balance after SIP: {balance}")

    return balance

def show_balance(account_number):
    # Get the account balance, FD balance, and SIP balance
    with open(ACCOUNTS_FILE, 'r') as f:
        for line in f:
            acc_num, name, pwd, balance = line.strip().split(',')
            if acc_num == account_number:
                print(f"Your Current Balance: {balance}")
                fd_balance = get_fd_balance(account_number)
                print(f"Your Fixed Deposit Balance: {fd_balance}")
                sip_balance = get_sip_balance(account_number)
                print(f"Your SIP Investment Balance: {sip_balance}")
                total_balance = float(balance) + fd_balance + sip_balance
                print(f"Your Total Balance (Savings + FD + SIP): {total_balance}")
                return

    print("Account not found.")

def main():
    while True:
        print("\nWelcome to the Banking System!")
        print("1. Create Account")
        print("2. Login")
        print("3. Forget Password")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            account_number, balance = login()
            if account_number:
                while True:
                    print("\n1. Deposit")
                    print("2. Withdraw")
                    print("3. Open Fixed Deposit")
                    print("4. Open SIP Investment")
                    print("5. Show Balance")
                    print("6. Close Fixed Deposit")
                    print("7. Logout")
                    transaction_choice = input("Enter your choice: ")

                    if transaction_choice == '1':
                        balance = deposit(account_number, balance)
                    elif transaction_choice == '2':
                        balance = withdraw(account_number, balance)
                    elif transaction_choice == '3':
                        balance = open_fixed_deposit(account_number, balance)
                    elif transaction_choice == '4':
                        balance = open_sip(account_number, balance)
                    elif transaction_choice == '5':
                        show_balance(account_number)
                    elif transaction_choice == '6':
                        close_fixed_deposit(account_number, balance)
                    elif transaction_choice == '7':
                        print("Logged out successfully!")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            forget_password()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

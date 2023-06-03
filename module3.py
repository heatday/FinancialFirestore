import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from tabulate import tabulate
import colorama
from colorama import Fore, Style
from pyfiglet import Figlet

# colorama colored output
colorama.init()

# font stylized header
font = Figlet(font='slant')

# Load Firebase credentials
cred = credentials.Certificate('D:/BYUI courses/cse310/week 07/Financial.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Get the users collection from Firestore
users_collection = db.collection('users')

# Function to register a user
def register_user():
    print(Fore.GREEN + font.renderText('Register a User') + Style.RESET_ALL)
    username = input('Username: ')
    email = input('Email: ')
    password = input('Password: ')

    user_data = {
        'username': username,
        'email': email,
        'password': password
    }
    users_collection.document(email).set(user_data)
    print('Successfully registered.')

# Function to authenticate a user
def authenticate_user():
    print(Fore.GREEN + font.renderText('Authenticate or Login a User') + Style.RESET_ALL)
    email = input('Email: ')
    password = input('Password: ')

    # Get the user from Firestore using the email
    user_doc = users_collection.document(email).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        if user_data['password'] == password:
            print('Login successful')
            return user_data
        else:
            print('Incorrect password')
    else:
        print('User not found')
    return None


# Function to update user profile
def update_profile(user_data):
    print(Fore.GREEN + font.renderText('Update Profile') + Style.RESET_ALL)

    # Check if the user wants to update the username
    update_username = input('Update Username? (Y/N): ')
    if update_username.upper() == 'Y':
        new_username = input('New Username: ')
        user_data['username'] = new_username

    # Check if the user wants to update the email
    update_email = input('Update Email? (Y/N): ')
    if update_email.upper() == 'Y':
        new_email = input('New Email: ')
        user_data['email'] = new_email

    # Check if the user wants to update the password
    update_password = input('Update Password? (Y/N): ')
    if update_password.upper() == 'Y':
        new_password = input('New Password: ')
        user_data['password'] = new_password

    # Check if the email is being updated
    if update_email.upper() == 'Y':
        # Create a new document with the new email
        users_collection.document(new_email).set(user_data)
        print('Profile updated.')

        # Delete the old document
        users_collection.document(user_data['email']).delete()
        print('Old profile deleted.')

        # Update user_data with the new email
        user_data['email'] = new_email
    else:
        # Update the existing document with the updated profile information
        users_collection.document(user_data['email']).set(user_data)
        print('Profile updated.')

    return user_data








# Function to insert income
def insert_income(email):
    while True:
        print(Fore.GREEN + font.renderText('Insert Income') + Style.RESET_ALL)
        user_doc = users_collection.document(email)
        # creates user collection in db
        income_collection = user_doc.collection('income')

        income_data = {
            'amount': float(input('Income Amount: ')),
            'description': input('Income Description: ')
        }
        #insert income to database
        income_collection.add(income_data)
        print('Income inserted.')

        choice = input('Do you want to add another income? (Y/N): ')
        if choice.upper() != 'Y':
            break

# Function to insert Expense
def insert_expenses(email):
    while True:
        print(Fore.GREEN + font.renderText('Insert Expenses') + Style.RESET_ALL)
        user_doc = users_collection.document(email)
        # creates user collection in db
        expenses_collection = user_doc.collection('expenses')

        expenses_data = {
            'amount': float(input('Expenses Amount: ')),
            'description': input('Expenses Description: ')
        }
        #insert expenses to database
        expenses_collection.add(expenses_data)
        print('Expenses inserted.')

        choice = input('Do you want to add another expense? (Y/N): ')
        if choice.upper() != 'Y':
            break




# Function to show table
def show_financial_info(email):
    print(Fore.GREEN + font.renderText('Show Financial Information') + Style.RESET_ALL)
    user_doc = users_collection.document(email)
    income_collection = user_doc.collection('income')
    expenses_collection = user_doc.collection('expenses')

    income_docs = list(income_collection.stream())
    expenses_docs = list(expenses_collection.stream())

    financial_data = []

    total_income = 0
    total_expenses = 0

    for doc in income_docs:
        data = doc.to_dict()
        total_income += data['amount']
        financial_data.append([data['amount'], '', data['description'], ''])

    for doc in expenses_docs:
        data = doc.to_dict()
        total_expenses += data['amount']
        financial_data.append(['', data['amount'], '', data['description']])

    average_income = total_income / len(income_docs) if len(income_docs) > 0 else 0
    average_expenses = total_expenses / len(expenses_docs) if len(expenses_docs) > 0 else 0
    net_income = total_income - total_expenses

    # table structure
    financial_data.append(['Total Income', 'Total Expenses', '', ''])
    financial_data.append([total_income, total_expenses, '', ''])
    financial_data.append(['Average Income', 'Average Expenses', '', ''])
    financial_data.append([average_income, average_expenses, '', ''])
    financial_data.append(['', 'Net Income', '', ''])
    financial_data.append(['', net_income, '', ''])

    # Store financial information in Firestore
    financial_info = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'average_income': average_income,
        'average_expenses': average_expenses,
        'net_income': net_income
    }
    user_doc.update(financial_info)

    headers = ["Income", "Expenses", "Income Description", "Expenses Description"]
    print('Financial Information')
    print(tabulate(financial_data, headers=headers, tablefmt="fancy_grid"))


def delete_profile(user_data):
    print(Fore.GREEN + font.renderText('Delete Profile') + Style.RESET_ALL)
    confirmation = input('Are you sure you want to delete your profile? (Y/N): ')

    if confirmation.upper() == 'Y':
        # Delete the user's profile document
        users_collection.document(user_data['email']).delete()
        print('Profile deleted.')
        return True
    else:
        print('Deletion canceled.')
        return False 

# App layout
def financial_app():
    print(Fore.RED + font.renderText('Welcome to Financial Firestore App') + Style.RESET_ALL)
    user_data = None

    while True:
        print(Fore.GREEN + ('\nOptions:') + Style.RESET_ALL)
        print(Fore.GREEN + '1. Register a User' + Style.RESET_ALL)
        print(Fore.GREEN + '2. Authenticate or Login a User' + Style.RESET_ALL)
        print(Fore.GREEN + '3. Exit' + Style.RESET_ALL)

        choice = input(Fore.CYAN + 'Enter your choice:' + Style.RESET_ALL)

        if choice == '1':
            register_user()
        elif choice == '2':
            user_data = authenticate_user()
            if user_data:
                while True:
                    print('\nOptions:')
                    print(Fore.GREEN + '1. Update Profile' + Style.RESET_ALL)
                    print(Fore.GREEN + '2. Insert Income' + Style.RESET_ALL)
                    print(Fore.GREEN + '3. Insert Expenses' + Style.RESET_ALL)
                    print(Fore.GREEN + '4. Show Financial Information' + Style.RESET_ALL)
                    print(Fore.GREEN + '5. Delete Profile' + Style.RESET_ALL)
                    print(Fore.GREEN + '5. Log Out' + Style.RESET_ALL)

                    inner_choice = input(Fore.CYAN + 'Enter your choice: ' + Style.RESET_ALL)

                    if inner_choice == '1':
                        user_data = update_profile(user_data)
                    elif inner_choice == '2':
                        insert_income(user_data['email'])
                    elif inner_choice == '3':
                        insert_expenses(user_data['email'])
                    elif inner_choice == '4':
                        show_financial_info(user_data['email'])
                    if inner_choice == '5':
                        if delete_profile(user_data):
                            print('Profile deleted. Logged out.')
                            user_data = None
                            break
                    elif inner_choice == '6':
                        print('Logged out.')
                        user_data = None
                        break
                    else:
                        print('Invalid choice. Please try again.')
            else:
                print('Authentication failed.')
        elif choice == '3':
            print('Exiting the application. Goodbye!')
            break
        else:
            print('Invalid choice. Please try again.')

financial_app()
from pathlib import Path
import json
from colorama import Fore, Style, init
from collections import UserDict
from datetime import datetime as dtdt, timedelta
import re

# Base Field class 
class Field:
    def __init__(self, value) -> str: # Class init
        self.value = value

    def __str__(self): 
        return str(self.value)

# Name class with validation
class Name(Field):
    def __init__(self, value): # Class init
        self.validate(value)
        super().__init__(value)

    def validate(self, value) -> str: # Validate name value
        if not value or not value.isalpha():
            raise ValueError("Name must contain only letters.")
        return value.capitalize() # Return mane with capital first letter
    
# Phone class with validation
class Phone(Field):
    def __init__(self, value): # Class init
        self.validate(value)
        super().__init__(value)

    def validate(self, value): # Validate phone value
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must be exactly 10 digits.")

# Record class
class Record:
    def __init__(self, name): # Class init
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Add phone function
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Del phone function
    def delete_phone(self, phone) -> bool:
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    # Edit phone function
    def edit_phone(self, old_phone, new_phone) -> bool:
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    # Find phone function
    def find_phone(self, phone) -> str:
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

# Birthday management class
class Birthday(Field):
    def __init__(self, value):
        try:
            if re.fullmatch(r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", value):
                self.value = dtdt.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Address book class
class AddressBook(UserDict):
    def add_record(self, record) -> str:
        self.data[record.name.value] = record

    def find(self, name) -> str:
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Updated function to get upcoming birthdays
    def get_upcoming_birthdays(self) -> list:
        upcoming = []
        today = dtdt.today().date()
        
        for record in self.data.values():
            # Only process records with a birthday set
            if record.birthday is None:
                continue

            # Extract the birthday date from the Birthday object
            bday = record.birthday.value.date()

            # Set the birthday for the current year
            upcoming_bday = bday.replace(year=today.year)
            
            # If the birthday has already passed this year, use next year
            if upcoming_bday < today:
                upcoming_bday = bday.replace(year=today.year + 1)
            
            # Calculate the number of days until the birthday
            diff = (upcoming_bday - today).days
            
            # Check if birthday is within the next 7 days (including today)
            if 0 <= diff < 7:
                # Adjust if the birthday falls on a weekend
                if upcoming_bday.weekday() == 5:  # Saturday
                    upcoming_bday += timedelta(days=2)
                elif upcoming_bday.weekday() == 6:  # Sunday
                    upcoming_bday += timedelta(days=1)
                
                # Append the record's name and the adjusted birthday date
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": upcoming_bday.strftime("%d.%m.%Y")
                })
        return upcoming

init(autoreset=True)
PHONEBOOK = 'contacts.json'
json_path = Path(PHONEBOOK)

# Error messages for ValueError
FUNC_LIST_VALUE_ERROR = {
    "add_contact": "To add a record please use: add [name] [phone]",
    "change_contact": "To change a record please use: change [name] [new phone]",
    "delete_contact": "To delete a record please use: delete [name]",
    "show_contact": "To show a record please use: show [name]",
}

# Error messages for KeyError
FUNC_LIST_KEY_ERROR = {
    "add_contact": "Key Error ADD", # Cannot imagine this case
    "change_contact": "Contact is not found in the phonebook. Can't change",
    "delete_contact": "Contact is not found in the phonebook. Can't delete",
    "show_contact": "Contact is not found in the phonebook. Can't show",
}

# Error messages for IndexError
FUNC_LIST_INDEX_ERROR = {
    "add_contact": "Index Error ADD", # Cannot imagine this case
    "change_contact": "Index Error CHANGE", # Cannot imagine this case
    "delete_contact": "To delete a record please use: delete [name]",
    "show_contact": "To show a record please use: show [name]",
}

# Text for 'help' command
HELP_TEXT = "Available commands:\n" \
"'hello' - Greets you, sir \n" \
"'add' - Adds new record to your phonebook " \
"Usage: 'add [name] [phone]'\n" \
"'change' - Changes existing record or adds new record (if none) to your phonebook " \
"Usage: 'change [name] [phone]'\n" \
"'show' - Shows existing record from your phonebook " \
"Usage: 'show [name]'\n" \
"'delete' - Deletes existing record from your phonebook " \
"Usage: 'delete [name]'\n" \
"'all' - Shows your phonebook \n" \
"'close', 'exit' or 'quit' - Exits this program :(\n" \
"'help' - Shows this text \n"

# Helper function to match function name for decorator
def func_name(func_name: str, error: str) -> str:
    
    # Check error value to select correct dictionary
    match error:
            case "Value_Error":
                list = FUNC_LIST_VALUE_ERROR
            case "Key_Error":
                list = FUNC_LIST_KEY_ERROR
            case "Index_Error":
                list = FUNC_LIST_INDEX_ERROR
    
    # Match function name to a dictionary key to get correct error message
    matched = next(filter(lambda k: k == func_name, list), None)
    
    if matched:
        return list[matched]

    return "Unknown command"

# Decorator function to catch errors
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return dir_file_color('WARN', func_name(func.__name__, "Value_Error"))
        except KeyError:
            return dir_file_color('WARN', func_name(func.__name__, "Key_Error"))
        except IndexError:
            return dir_file_color('WARN', func_name(func.__name__, "Index_Error"))
        
    return inner

# Function to print filenames and directories in different colors
def dir_file_color(lvl: str, message: str):
    # Dictionary for different colors (c) S. Kodenko ;)
    COLORS={
        'CHANGE'    :Fore.BLUE,
        'ADD'       :Fore.GREEN,
        'DELETE'    :Fore.RED,
        'WARN'      :Fore.YELLOW
    }
    if lvl in COLORS.keys():
        return f"{COLORS[lvl]} {message} {Style.RESET_ALL}"
    else:
        return f"{Fore.WHITE} {message} {Style.RESET_ALL}"
    
# Function to parse input commands
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Decorated add contact function
@input_error
def add_contact(args, contacts) -> str:
    name, phone = args
    contacts[name] = phone
    return dir_file_color('ADD', f"Contact {name} added.")

# Decorated change contact function
@input_error
def change_contact(args, contacts) -> str:
    name, phone = args
    contacts[name] = phone
    return dir_file_color('CHANGE', f"Contact {name} changed.")

# Decorated delete contact function
@input_error
def delete_contact(args, contacts) -> str:
    if not args:
        raise IndexError("No name provided")
    name = args[0]
    del contacts[name]
    return dir_file_color('DELETE', f"Contact {name} deleted")

# Decorated show contact function
@input_error    
def show_contact(args, contacts):
    if not args:
        raise IndexError("No name provided")
    name = args[0]
    print(f"1. {Fore.WHITE} {name}: \t {Fore.MAGENTA} {contacts[name]} {Style.RESET_ALL}") 

# Print phonebook function    
def print_contacts(contacts: dict):
     print("Your existing contacts, sir:")
     i = 0
     for key, value in contacts.items():
        i += 1
        print(f"{i}. {Fore.WHITE} {key}: \t {Fore.MAGENTA} {value} {Style.RESET_ALL}")  

# Show help for 'help' command
def show_help():
    print(HELP_TEXT)

# Main program
def main():
    
    # Read saved phonebook (.json file version)
    if json_path.exists():
        with open(PHONEBOOK, "r") as json_file:
            contacts = json.load(json_file)
            print_contacts(contacts)
    else:
        contacts = {}

    # Welcome message
    print("Welcome to the assistant bot!")
    print("Please use 'help' command for more information")
    print()

    # Endless cycle to await commands
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        # Command execution block
        if command in ["close", "exit", "quit"]:
            sorted_contacts = {k: contacts[k] for k in sorted(contacts)}
            with open(PHONEBOOK, "w") as json_file:
                json.dump(sorted_contacts, json_file, indent=4)
                print("Phonebook is saved. Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "delete":
            print(delete_contact(args, contacts))
        elif command == "show":
            print(show_contact(args, contacts))   
        elif command == "all":
            print_contacts(contacts)
        elif command == "help":
            show_help()    
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()


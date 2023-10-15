from datetime import datetime
from collections import UserDict
import pickle
from sort import clean_folder_interface
from note import notebook_interface, Note
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADDRESS_BOOK_PATH = os.path.join(BASE_DIR, 'address_book.dat')
class Field:
    def __init__(self, value=None):
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

# 15.10.23 Olga
class Phone(Field): #15.10.2023 Внесла изменения: проверка формата номера телефона (Оля)
   
    def get_value(self): # 15.10.23  Yulia
        return str(self.value)
    
    def __str__(self):
        return str(self.value)
    
    def set_value(self, value):
        validated_phone = self.validate_phone(value) # 15.10.23 modify Yulia
        if validated_phone is None: # 15.10.23 modify Yulia
        # if self.validate_phone(value) == False:
            print("Invalid phone number format")  # check phone
        else:
            self.value = validated_phone

    @staticmethod
    def validate_phone(phone):
        new_phone = (
            str(phone).strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        if new_phone.startswith("38") and len(new_phone) == 12:  # 15.10.23 modify Yulia
            return "+" + new_phone
        elif len(new_phone) == 10:
            return '+38' + new_phone
        # elif len(new_phone) == 12 and new_phone.startswith("38"):   # 15.10.23 Olga
        #     return '+' + new_phone
        else:
            return None # 15.10.23 modify Yulia
        



# 15.10.23 Yulia
class EmailAddress(Field):
    def __init__(self, value=None):
        super().__init__(value)

    def set_value(self, value):
        # Add your email validation logic here
        if isinstance(value, str) and self.validate_email(value):
            self.value = value
        else:
            print("Invalid email format")

    def get_value(self):
        return self.value

    @staticmethod
    def validate_email(email):
        # Add your email validation logic here
        # For simplicity, let's check if "@" is in the email
        return "@" in email if email else False




class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    def set_value(self, value):
        try:
            datetime.strptime(value, "%d.%m.%y")
        except ValueError:
            raise ValueError("Invalid date format. Please use 'dd.mm.yy' format.")

        self.value = value

    def days_to_birthday(self):
        if self.value is None:
            return None
        birth_date = datetime.strptime(self.value, "%d.%m.%y").date()
        current_date = datetime.now().date()  # Use only the date part

        # Calculate next birthday date
        next_birthday_year = current_date.year
        if (current_date.month, current_date.day) > (birth_date.month, birth_date.day):
            next_birthday_year += 1

        next_birthday_date = datetime(next_birthday_year, birth_date.month, birth_date.day).date()

        difference = next_birthday_date - current_date
        days_until_birthday = difference.days

        return days_until_birthday

class Record:
    
    
    def __init__(self, name, birthday=None, email=None):
        self.name = Name(name)
        self.phones = []
        self.emails = [] if email else [EmailAddress(email)]
        self.birthday = Birthday(birthday)

    def add_email(self, email):
        self.emails.append(EmailAddress(email))

    
    def get_emails(self):
        if hasattr(self, 'emails'):
            return [email for email in self.emails if email and isinstance(email, EmailAddress)] if self.emails else []
        elif hasattr(self, 'email'):
            return [self.email] if self.email and isinstance(self.email, EmailAddress) else []
        else:
            return []



    
    def add_phone(self, phone):
        if isinstance(phone, Phone):  
            self.phones.append(phone)
        elif Phone.validate_phone(phone):
            phone_value = Phone.validate_phone(phone)
            if phone_value:
                self.phones.append(Phone(phone_value))
            else:
                raise ValueError("Invalid phone number format")
        else:
            raise ValueError("Invalid phone number format")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, phone, new_phone):
        for p in self.phones:
            if p.value == phone:
                p.set_value(new_phone)
                break
        else:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    
# 15.10.23 Yulia
    def get_email(self):
        return self.email.get_value() if self.email else None

class AddressBook(UserDict):
    def __init__(self, filename):
        super().__init__()
        self.page_size = 10
        self.filename = filename

    def add_record(self, record):
        self.data[record.name.get_value()] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self):
        records = list(self.data.values())
        for i in range(0, len(records), self.page_size):
            yield records[i:i + self.page_size]

    def save_to_file(self):
        try:
            with open(self.filename, 'wb') as file:
                pickle.dump(self.data, file)
            print(f'Address book saved to {self.filename}')
        except Exception as e:
            print(f'Error saving to {self.filename}: {str(e)}')

    def read_from_file(self):
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
                self.data = data
            print(f'Address book loaded from {self.filename}')
        except FileNotFoundError:
            print(f'File {self.filename} not found. Creating a new address book.')
        except Exception as e:
            print(f'Error reading from {self.filename}: {str(e)}')

    def search(self, query):
        query = query.lower()
        results = []
        for record in self.data.values():
            if query in record.name.get_value().lower():
                results.append(record)
            for phone in record.phones:
                if query in phone.get_value():
                    results.append(record)
        return results
    #15.10.23 Yulia
    def delete_contact(self, name):
        """
        Delete a contact by name.
        """
        if name in self.data:
            del self.data[name]
            print(f"Contact {name} deleted.")
        else:
            print(f"Contact {name} not found.")


def handle_command(address_book, command):
    action, *args = command.lower().split()

    # 15.10.23 Nazar
    if action == "add":
        if len(args) < 2:
            return "Invalid format for 'add'. Please provide a name and at least one phone number."
        name = args[0]
        phones = []
        email = None
        birthday = None

        # 15.10.23 Yulia
        # Separate phones, email, and birthday
        for arg in args[1:]:
            if "@" in arg:
                email = arg
            elif len(arg.split('.')) == 3:
                birthday = arg
            else:
                phones.append(arg)

        record = Record(name, birthday, email)

        for phone in phones:
            phone_value = Phone.validate_phone(phone)
            if phone_value:
                phone_obj = Phone(phone_value)
                record.add_phone(phone_obj)
            else:
                return "Invalid phone number format"

        # Add email if present
        if email:
            record.add_email(email)

        address_book.add_record(record)

        # 15.10.23 Yulia
        phones_str = ', '.join([str(p.get_value()) for p in record.phones])
        email_str = ', '.join([str(email.get_value()) for email in record.get_emails()])
        birthday_str = record.birthday.get_value() or "N/A"  # Use "N/A" if birthday is None
        response = f"Contact {name} added with the following information:\n" \
                f"Name: {record.name.get_value()}\n" \
                f"Phone: {phones_str}\n" \
                f"Email: {email_str}\n" \
                f"Birthday: {birthday_str}"

        # 14.10.23 Nazar
        # If birthday is present, calculate and append days until next birthday
        if birthday:
            days_left = record.birthday.days_to_birthday()
            if days_left is not None:
                response += f"\n{days_left} days left until the next birthday."

        return response

    elif action == "delete":
        if len(args) < 1:
            return "Invalid format for 'delete' command. Please provide a name."
        name = args[0]
        address_book.delete_contact(name)
        return ""
    

# 14.10.23 Alex
    elif action == "notebook":
        notebook_interface()
        return "Work with notebook is completed."




    elif action == "birthday" and args[0]:
        if len(args) < 2:
            return "Invalid format for 'add birthday' command. Please provide a name and a birthday date."
        name = args[0]
        birthday = args[1]
        record = Record(name, birthday)
        address_book.add_record(record)
        response = f"Contact {name} added with birthday: {birthday}"
        days_left = record.birthday.days_to_birthday()
        if days_left is not None:
            response += f"\n{days_left} days left until the next birthday."
        return response



# 15.10.23 Nazar

    elif action == "change":

        if len(args) < 2:
            return "Invalid format for 'change' command. Please provide a name and either a new phone number or a new birthday."

        name = args[0]
        record = address_book.find(name)
        if record:
            if len(args[1].split('.')) == 3:
                new_birthday = args[1]
                record.birthday.set_value(new_birthday)
                return f"Contact {name} birthday changed to {new_birthday}"

            else:
                new_phone = args[1]
                record.edit_phone(record.phones[0].get_value(), new_phone)
                return f"Contact {name} phone number changed to {new_phone}"
        else:
            return f"Contact {name} not found"
        


# 15.10.23 Nazar
    elif action == "find":
        if len(args) < 1:
            return "Invalid format for 'find' command. Please provide a search query."
        search_query = ' '.join(args)
        results = address_book.search(search_query)

        if results:
            contacts_info = []
            for record in results:
                phones_str = ', '.join([p.get_value() for p in record.phones])
                info = f"{record.name.get_value()}: {phones_str} | {record.birthday.get_value()}"

                # Check if birthday is present
                if record.birthday.get_value():
                    days_left = record.birthday.days_to_birthday()
                    birthday_info = f" | Birthday in {days_left} days" if days_left is not None else ""
                    info += birthday_info
                contacts_info.append(info)
            return "\n".join(contacts_info)

        else:

            return f"No contacts found for '{search_query}'"


# 15.10.23 Nazar
    elif action == "phone":
        if len(args) < 1:
            return "Invalid format for 'phone' command. Please provide a name."
        name = args[0]
        record = address_book.find(name)
        if record:
            phones_str = ', '.join([p.get_value() for p in record.phones])
            birthday_info = ""
            # Check if birthday is present
            if record.birthday.get_value():
                days_left = record.birthday.days_to_birthday()
                birthday_info = f" | Birthday in {days_left} days" if days_left is not None else ""
            return f"Phone number for {name}: {phones_str} | {record.birthday.get_value()} {birthday_info}"

        else:
            return f"Contact {name} not found"

# 14.10.23 Nazar
    elif action == "show" and args[0] == "all":
        if not address_book.data:
            return "No contacts found"
        else:
            contacts_info = []
            for name, record in address_book.data.items():
                phones_str = ', '.join([str(p.get_value()) for p in record.phones])
                emails_str = ', '.join([email.get_value() for email in (record.get_emails() or []) if email])
                info = f"{name}: {phones_str} | {emails_str} | {record.birthday.get_value()}"
                
                # Check if birthday is present
                if record.birthday.get_value():
                    days_left = record.birthday.days_to_birthday()
                    if days_left is not None:
                        info += f" | {days_left} days left until the next birthday."
                contacts_info.append(info)
            return "\n".join(contacts_info)
        

    elif action == "celebration" and args and args[0] == "in":
        if len(args) < 2 or not args[1].isdigit():
            return "Invalid format for 'celebration in' command. Please provide a valid number of days."

        days_until_celebration = int(args[1])
        upcoming_birthdays = []
        for record in address_book.data.values():
            if record.birthday.get_value():
                days_left = record.birthday.days_to_birthday()
                if days_left is not None and days_left <= days_until_celebration:
                    phones_str = ', '.join([p.get_value() for p in record.phones])
                    upcoming_birthdays.append(f"{record.name.get_value()}: {phones_str} | {record.birthday.get_value()}. Don't forget to greet!")

        if upcoming_birthdays:
            return f"Upcoming birthdays in the next {days_until_celebration} days:\n" + "\n".join(upcoming_birthdays)
        else:
            return f"No upcoming birthdays in the next {days_until_celebration} days."
            
        


#14.10.23 Nazar
    elif action == "helper":
        return (
            "Available commands:\n"
            "  - add [name] [phone][birthday] [emai]: Add a new contact with optional phones and birthday.\n"
            "  - show all: Display all contacts with phones and optional days until the next birthday.\n"
            "  - celebration in [days]: Show upcoming birthdays in the next [days] days with names and phones.\n"
            "  - helper: Display available commands and their descriptions.\n"
            "  - find [letter] or [number]: Display all contacts with letter or number, which you saied about.\n"
            "  - change [name] [phone] or [birthday]: Changes contact, which you want.\n"
            "  - phone [name]: phoning person you want.\n"
            "  - delete [name]: Delete a contact by name.\n"  #15.10.23 Yuliya
            "  - goodbye, close, exit: Save the address book to a file and exit the program.\n"
            "  - clean: Open sorter.\n"  #15.10.23 Alex
            "  - notebook: Open notes.\n" #15.10.23 Alex

        )



    elif action == "hello":
        return "How can I help you?"

    elif action in ["goodbye", "close", "exit"]:
        return "Good bye!"

    elif action == "clean":
        clean_folder_interface()
        return "Cleaning completed."

    else:
        return "Unknown command"

def main():
    filename = "address_book.dat"
    address_book = AddressBook(filename)
    address_book.read_from_file()

    print("Welcome to ContactBot!")

    # Print the number of contacts loaded
    print(f"Address book loaded from {filename}. {len(address_book.data)} contacts found.") # 15.10.23 modify Yulia

    while True:
        command = input("Enter a command: ").strip()

        if command.lower() in ["goodbye", "close", "exit"]:
            address_book.save_to_file()  # Save the data before exiting
            print("Good bye!")
            break

        response = handle_command(address_book, command)
        print(response)

if __name__ == "__main__":
    main()
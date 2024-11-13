import json
import random
import re
import os
import sys
from re import match

# Global configuration
HOW_MANY_BOOKS = 3
LINE = 128
PAGE = 64

# Global state
pages = {}
page_number = 0
line_window = {}
line_number = 0
char_window = []


def clean_line(line):
    """Remove multiple whitespaces, handle dashes, and add space at end of lines."""
    return line.strip().replace('-', '') + ' '


def process_char(char):
    """Accumulate characters into lines."""
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()


def add_line():
    """Add completed line to the current page."""
    global char_window, line_number
    line_number += 1
    process_page(''.join(char_window), line_number)
    char_window.clear()


def process_page(line, line_num):
    """Accumulate lines into pages."""
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()


def add_page():
    """Add completed page to the book."""
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0


def read_book(file_path):
    """Read and process a book file line by line."""
    global char_window
    with open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = clean_line(line)
            if line.strip():
                for c in line:
                    process_char(c)
    # Handle any remaining incomplete buffers
    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()


def process_books(*paths):
    """Process multiple book files."""
    for path in paths:
        read_book(path)


def generate_code_book():
    """Create mapping of characters to their locations in the processed books."""
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
    return code_book


def save(file_path, book):
    """Save codebook to JSON file."""
    with open(file_path, 'w') as fp:
        json.dump(book, fp)


def load(file_path, *key_books, reverse=False):
    """Load or generate codebook from books."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        process_books(*key_books)
        if reverse:
            save(file_path, pages)
            return pages
        else:
            code_book = generate_code_book()
            save(file_path, code_book)
            return code_book


def encrypt(code_book, message):
    """Encrypt a message using the codebook."""
    cipher_text = []
    for char in message:
        if char not in code_book:
            continue  # Skip characters not in codebook
        index = random.randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return '-'.join(cipher_text)


def decrypt(rev_code_book, ciphertext):
    """Decrypt a message using the reverse codebook."""
    plaintext = []
    for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
        page, line, char = cc.split('-')
        plaintext.append(rev_code_book[page][line][int(char)])
    return ''.join(plaintext)


def main_menu():
    """Display and handle main menu options."""
    print("""1). Encrypt
2). Decrypt
3). Quit
""")
    return int(input("Make a selection [1,2,3]: "))


def main():
    """Main program loop."""
    key_books = ('books/War_and_Peace.txt', 'books/Moby_Dick.txt', 'books/Dracula.txt')
    code_book_path = 'code_books/dmdwp.txt'
    rev_code_book_path = 'code_books/dmdwp_r.txt'

    while True:
        try:
            choice = main_menu()
            if choice == 1:
                code_book = load(code_book_path, *key_books)
                message = input("Please enter your secret message: ")
                print(encrypt(code_book, message))
            elif choice == 2:
                rev_code_book = load(rev_code_book_path, *key_books, reverse=True)
                message = input("Please enter your cipher text: ")
                print(decrypt(rev_code_book, message))
            elif choice == 3:
                sys.exit(0)
            else:
                print("Invalid selection. Please choose 1, 2, or 3.")
        except ValueError:
            print("Improper selection. Please enter a number.")


if __name__ == '__main__':
    main()
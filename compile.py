import os
import subprocess
from colorama import Fore, Style

MARKDOWN_DIR = 'markdown'
PDF_DIR = 'pdf'

if not(os.path.exists(PDF_DIR) and os.path.isdir(PDF_DIR)):
    print(f'{Style.DIM}Creating /pdf directory... {Style.RESET_ALL}')
    os.mkdir(PDF_DIR)


markdown_list = [file for file in os.listdir(MARKDOWN_DIR) \
        if file.endswith('.md')]

print(Style.BRIGHT + "Generating PDF files..." + Style.RESET_ALL)
for md_file in markdown_list:
    n = len(md_file)
    pdf_file = md_file[:n-2]+'pdf'
    print(f'{Fore.CYAN}    --> Generating {pdf_file}{Fore.RED}')
    command = f'pandoc {MARKDOWN_DIR}/{md_file} -o {PDF_DIR}/{pdf_file}'
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, \
            text=True)

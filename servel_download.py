import re
import os
import requests
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
from pathlib import Path


# Variables
url_padron = "https://www.servel.cl/padron-electoral-auditado-plebiscito-nacional-2020/"
output_folder = "output"


# Open and parse page
request = requests.get(url_padron)
page = BeautifulSoup(request.text, 'lxml')


# Find all PDF files links
main_content = page.find(class_='tab-content')
links = main_content.find_all('a', href=re.compile("pdf"))

full_links = []

for link in links:
    full_link = urljoin(url_padron, link['href'])
    full_links.append(full_link)

print("Found " + str(full_links.count) + " links")


# Download each file in the output directory
cwd = os.getcwd()
output_path = cwd + '/' + output_folder
Path(output_path).mkdir(exist_ok=True)

for full_link in full_links:
    print("Downloading " + full_link)
    local_filename = full_link.split('/')[-1]

    with requests.get(full_link, stream=True) as r:
        with open(output_path + '/' + local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

print("End")

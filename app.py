from optomize.main import Optomize
import os
import urllib.request
import chardet
import validators

html_url=""
cwd=""


def process_url(html_url):
    if(html_url.find('http') == -1 and html_url.find('www') != -1):
        html_url = 'https://'+html_url
    elif(html_url.find('http') == -1 and html_url.find('www') == -1):
        html_url = 'https://www.' + html_url
    return html_url


def create_html_file():
    html_url = process_url(input("Please enter site URL: "))
    if validators.url(html_url):
        try:
            html_file_bytes = urllib.request.urlopen(html_url)
        except Exception as e:
            print(e)
        html_byte_array = html_file_bytes.read()
        encoding_type = chardet.detect(html_byte_array)
        html_str = html_byte_array.decode(encoding_type['encoding'])
        html_write = open(os.getcwd()+"/optomize/files/html_file.html", "w")
        html_write.write(html_str)
        html_write.close()
        html_file_bytes.close()
    else:
        print("Error: Incorrect url format")


def main():
    create_html_file()
    

if __name__ == "__main__":
    main()
    cwd = os.getcwd()
    html_path = cwd+"/optomize/files/html_file.html"
    css_path = cwd+"/optomize/files/styling.css"
    opt = Optomize(html_path, css_path)
    opt.run()
import requests as std_requests
from bs4 import BeautifulSoup
import sys

#========================================
# OUO BYPASS, adapted from https://github.com/xcscxr/ouo-bypass/blob/main/ouo-bypass.py
import re
from curl_cffi import requests as curl_requests
from urllib.parse import urlparse

def RecaptchaV3():
    ANCHOR_URL = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe'
    url_base = 'https://www.google.com/recaptcha/'
    post_data = "v={}&reason=q&c={}&k={}&co={}"
    client = std_requests.Session()
    client.headers.update({
        'content-type': 'application/x-www-form-urlencoded'
    })
    matches = re.findall(r'([api2|enterprise]+)\/anchor\?(.*)', ANCHOR_URL)[0]
    url_base += matches[0]+'/'
    params = matches[1]
    res = client.get(url_base+'anchor', params=params)
    token = re.findall(r'"recaptcha-token" value="(.*?)"', res.text)[0]
    params = dict(pair.split('=') for pair in params.split('&'))
    post_data = post_data.format(params["v"], token, params["k"], params["co"])
    res = client.post(url_base+'reload', params=f'k={params["k"]}', data=post_data)
    answer = re.findall(r'"rresp","(.*?)"', res.text)[0]    
    return answer

# -------------------------------------------

client = curl_requests.Session()
client.headers.update({
    'authority': 'ouo.io',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'referer': 'http://www.google.com/ig/adde?moduleurl=',
    'upgrade-insecure-requests': '1',
})

# -------------------------------------------

def ouo_bypass(url):
    tempurl = url.replace("ouo.press", "ouo.io")
    p = urlparse(tempurl)
    id = tempurl.split('/')[-1]
    res = client.get(tempurl, impersonate="chrome110")
    next_url = f"{p.scheme}://{p.hostname}/go/{id}"

    for _ in range(2):
        if res.headers.get('Location'):
            break

        bs4 = BeautifulSoup(res.content, 'html.parser')  # Changed to 'html.parser'
        form = bs4.find("form")
        if form is None:
            break

        inputs = form.find_all("input", {"name": re.compile(r"token$")})
        data = {input.get('name'): input.get('value') for input in inputs}
        data['x-token'] = RecaptchaV3()
        
        h = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        
        res = client.post(next_url, data=data, headers=h, allow_redirects=False, impersonate="chrome110")
        next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"

    return res.headers.get('Location')
#========================================

def fetch_page(url):
    """Fetches content of the given URL."""
    response = std_requests.get(url)
    response.raise_for_status()  # Check that the request was successful
    return response.text

def find_matching_links(html, keyword):
    """Finds all <a> tags that include the keyword in their text and returns their URLs."""
    soup = BeautifulSoup(html, 'html.parser')
    return [(a.text.strip(), a['href']) for a in soup.find_all('a', href=True) if keyword.lower() in a.text.lower()]

def extract_desired_info(html):
    """Extracts and formats specific information from the given URL by parsing relevant content blocks."""
    soup = BeautifulSoup(html, 'html.parser')
    output_data = []

    # Extract the main title and other details
    title_element = soup.find('p', class_='has-text-align-left has-very-light-gray-background-color has-background has-medium-font-size')
    if title_element:
        # Extract all strong tags and subsequent texts clearly
        strong_tags = title_element.find_all('strong')
        for strong_tag in strong_tags:
            key = strong_tag.get_text(strip=True).replace(":", "")
            value = strong_tag.next_sibling.strip()
            output_data.append(f"{key}: {value}")
        output_data.append("")  # Add a blank line after the details section

    # Extracting and organizing download links
    sections = soup.find_all('div', class_='wp-block-columns')
    for section in sections:
        section_title_tag = section.find('p', class_='has-text-align-center has-medium-font-size')
        if section_title_tag and section_title_tag.strong:
            section_title = section_title_tag.strong.get_text(strip=True)
            output_data.append(section_title)
        
        p_tags = section.find_all('p')
        for p_tag in p_tags:
            strong_tag = p_tag.find('strong')
            if strong_tag:
                provider = strong_tag.get_text(strip=True)
                a_tag = p_tag.find('a')
                if a_tag:
                    link_href = a_tag['href']
                    #output_data.append(f"  {provider}: {link_href}")

                    # OUO BYPASS mod
                    output_data.append(f"  {provider}: {ouo_bypass(link_href)}")
            else:
                a_tags = p_tag.find_all('a')
                for a_tag in a_tags:
                    provider = a_tag.get_text(strip=True)
                    link_href = a_tag['href']
                    #output_data.append(f"  {provider}: {ouo_bypass(link_href)}")

                    # OUO BYPASS mod
                    output_data.append(f"  {provider}: {ouo_bypass(link_href)}")

        output_data.append("")  # Add a blank line after each section

    return "\n".join(output_data).strip()  # Ensure no extra blank lines at the end


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nx_search.py <keyword>")
        sys.exit(1)

    url = "https://exemple.com"
    keyword = sys.argv[1]

    initial_html = fetch_page(url)
    matching_links = find_matching_links(initial_html, keyword)

    if matching_links:
#        print(f"Found {len(matching_links)} matching links:")
        if len(matching_links) > 1:
            for i, (text, link) in enumerate(matching_links):
                print(f"{i + 1}: {text}")

        if len(matching_links) > 1:
            print("")
            choice = input("Which number (anything else to quit): ")
            try:
                choice = int(choice) - 1
                if choice < 0 or choice >= len(matching_links):
                    sys.exit(1)
            except ValueError:
                sys.exit(1)
        else:
            choice = 0

        selected_link = matching_links[choice][1]
        try:
            print("")
            page_html = fetch_page(selected_link)
            data = extract_desired_info(page_html)
            print(data)
            print("")
        except Exception as e:
            print(f"Failed to process {selected_link}: {e}")
    else:
        print("No matching links found.")

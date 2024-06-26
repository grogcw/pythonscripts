import requests
from bs4 import BeautifulSoup
import sys

def fetch_page(url):
    """Fetches content of the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def find_matching_links(html, keyword):
    """Finds all <a> tags that include the keyword in their text and returns their URLs."""
    soup = BeautifulSoup(html, 'html.parser')
    return [(a.text.strip(), a['href']) for a in soup.find_all('a', href=True) if keyword.lower() in a.text.lower()]

def extract_desired_info(html):
    """Extracts and formats specific information from the given URL by parsing relevant content blocks."""
    soup = BeautifulSoup(html, 'html.parser')
    output_data = []

    title_element = soup.find('p', class_='has-text-align-left has-very-light-gray-background-color has-background has-medium-font-size')
    if title_element:
        strong_tags = title_element.find_all('strong')
        for strong_tag in strong_tags:
            key = strong_tag.get_text(strip=True).replace(":", "")
            value = strong_tag.next_sibling.strip()
            output_data.append(f"{key}: {value}")
        output_data.append("")

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
                    output_data.append(f"  {provider}: {link_href}")
            else:
                a_tags = p_tag.find_all('a')
                for a_tag in a_tags:
                    provider = a_tag.get_text(strip=True)
                    link_href = a_tag['href']
                    output_data.append(f"  {provider}: {link_href}")
        output_data.append("")

    return "\n".join(output_data).strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nx_search.py <keyword>")
        sys.exit(1)

    url = "https://<exemple>.com/"
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

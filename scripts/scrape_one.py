
from scrapling.fetchers import Fetcher
from pathlib import Path

# Use one product URL that you are permitted to access.
url = input("Enter the product URL: ").strip()

if not url.startswith("https://www.amazon.in/"):
    raise ValueError("Please enter an Amazon India product URL.")

page = Fetcher.get(url, follow_redirects=True)

print("Page retrieved.")
print("Response status:", page.status)

# Save the retrieved HTML for inspection.
output_file = Path("amazon_product_page.html")
output_file.write_text(page.html_content, encoding="utf-8")

print("HTML saved to:", output_file.resolve())

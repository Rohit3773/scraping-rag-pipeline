# wikipedia_scraper.py

import os
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class WikipediaScraperPDFGenerator:
    def __init__(self, urls=None, output_path="DOCS/scraped_data.pdf"):
        self.urls = urls or {
            "Generative AI": "https://en.wikipedia.org/wiki/Generative_artificial_intelligence",
            "AGI": "https://en.wikipedia.org/wiki/Artificial_general_intelligence",
            "RAG": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
            "LLM": "https://en.wikipedia.org/wiki/Large_language_model"
        }
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def scrape_page(self, url):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            paragraphs = soup.select("p")
            return "\n".join(p.get_text() for p in paragraphs if p.get_text(strip=True))
        except Exception as e:
            return f"[ERROR scraping {url}]: {e}"

    def scrape_all(self):
        scraped_data = {}
        for title, url in self.urls.items():
            print(f"Scraping: {title}")
            scraped_data[title] = self.scrape_page(url)
        return scraped_data

    def create_pdf(self, text_dict):
        c = canvas.Canvas(self.output_path, pagesize=letter)
        width, height = letter
        text_obj = c.beginText(40, height - 50)
        text_obj.setFont("Times-Roman", 12)

        for title, content in text_dict.items():
            text_obj.textLine(f"## {title} ##")
            for line in content.split("\n"):
                text_obj.textLine(line)
            text_obj.textLine("\n" * 2)

        c.drawText(text_obj)
        c.save()
        print(f"PDF created: {self.output_path}")
        return self.output_path

    def run(self):
        data = self.scrape_all()
        return self.create_pdf(data)

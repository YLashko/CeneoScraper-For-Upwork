from app.utils import extract_element
from app.models.opinion import Opinion
import requests
import json
from bs4 import BeautifulSoup

class Product:
    def __init__(self, product_id, product_name = None, opinions = []):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions = opinions.copy()
        self.number_of_opinions = 0
        self.pros_count = 0
        self.cons_count = 0
        self.score = 0
    
    def extract_product(self):
        next_page = "https://www.ceneo.pl/{}#tab=reviews".format(self.product_id)
        while next_page:
            respons = requests.get(next_page)
            page_dom = BeautifulSoup(respons.text, "html.parser")
            if self.product_name == None:
                self.product_name = page_dom.find("h1", class_="product-top__product-info__name js_product-h1-link js_product-force-scroll js_searchInGoogleTooltip default-cursor").text       
            opinions = page_dom.select("div.js_product-review") 
            self.number_of_opinions += len(opinions)
            for opinion in opinions:
                self.opinions.append(Opinion().extract_opinion(opinion).transform_opinion())
                self.pros_count += self.opinions[-1].pros_count
                self.cons_count += self.opinions[-1].cons_count
                self.score += self.opinions[-1].stars
            try:
                next_page = "https://www.ceneo.pl" + \
                    page_dom.select("a.pagination__next").pop()["href"]
            except IndexError:
                next_page = None
        self.score = round(self.score / self.number_of_opinions, 2)

    def __str__(self):
        return f"product_id: {self.product_id}<br>product_name: {self.product_name}<br>opinions:<br>" + "<br><br>".join(str(opinion) for opinion in self.opinions)

    def __repr__(self):
        return f"Product(product_id={self.product_id}, product_name={self.product_name}, opinions=[" + ", ".join(opinion.__repr__() for opinion in self.opinions) + "])"

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "number_of_opinions": self.number_of_opinions,
            "pros_count":self.pros_count,
            "cons_count":self.cons_count,
            "score":self.score,
            "opinions": [opinion.to_dict() for opinion in self.opinions]
        }

    def save_to_json(self):
        with open(f"app/products/{self.product_id}.json", "w", encoding="UTF-8") as fp:
            json.dump(self.to_dict(), fp, indent=4, ensure_ascii=False)

    def read_from_json(self):
        with open(f"app/products/{self.product_id}.json", "r", encoding="UTF-8") as fp:
            prod = json.load(fp)
        self.product_name = prod['product_name']
        opinions = prod['opinions']
        for opinion in opinions:
            self.opinions.append(Opinion(**opinion))

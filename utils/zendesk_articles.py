import base64
import requests
import json
from bs4 import BeautifulSoup
from typing import List

from llama_index.readers.schema.base import Document


class ZendeskAPI:
    """Class for interacting with the Zendesk API and reading data from a Zendesk workspace."""

    def __init__(
        self,
        email: str,
        token: str,
        zendesk_subdomain: str,
        locale: str = "en-us",
    ):
        self.email = email
        self.token = token
        self.zendesk_subdomain = zendesk_subdomain
        self.locale = locale

    def _get_headers(self):
        credentials = f"{self.email}/token:{self.token}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
        }

    def load_data(self) -> List[Document]:
        """Load data from the Zendesk workspace."""
        results = []
        articles = self.get_all_articles()
        for article in articles:
            body = article["body"]
            if body is None:
                continue
            soup = BeautifulSoup(body, "html.parser")
            body = soup.get_text()
            extra_info = {
                "id": article["id"],
                "title": article["title"],
                "url": article["html_url"],
                "updated_at": article["updated_at"],
            }
            results.append(
                Document(
                    text=body,
                    extra_info=extra_info,
                )
            )
        return results

    def get_all_articles(self):
        """Retrieve all articles from the Zendesk workspace."""
        articles = []
        next_page = None
        while True:
            response = self.get_articles_page(next_page)
            articles.extend(response["articles"])
            next_page = response["next_page"]
            if next_page is None:
                break
        return articles

    def get_articles_page(self, next_page: str = None):
        """Get a page of articles from Zendesk."""
        if next_page is None:
            url = f"https://{self.zendesk_subdomain}.zendesk.com/api/v2/help_center/{self.locale}/articles.json?per_page=100"
        else:
            url = next_page

        response = requests.get(url, headers=self._get_headers())
        response_json = json.loads(response.text)
        next_page = response_json.get("next_page", None)
        articles = response_json.get("articles", [])
        return {"articles": articles, "next_page": next_page}


loader = ZendeskAPI(
    email="your_email", token="your_token", zendesk_subdomain="subdomain_name"
)

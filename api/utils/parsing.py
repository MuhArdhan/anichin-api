from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv
from requests import Session
import dns.resolver
import socket

load_dotenv()


class Parsing(Session):
    def __init__(self) -> None:
        super().__init__()
        self.url = getenv("HOST", "")
        self.history_url = None
        self.user_agent = getenv("USER_AGENT", "")
        self.dns = getenv("DNS", "8.8.8.8")  # default Google DNS

        # Set default headers
        if self.user_agent:
            self.headers.update({"User-Agent": self.user_agent})

    def resolve_with_custom_dns(self, hostname):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns]
        answer = resolver.resolve(hostname, "A")
        return answer[0].to_text()

    def __get_html(self, slug, **kwargs):
        if slug.startswith("/"):
            url = f"{self.url}{slug}"
        else:
            url = f"{self.url}/{slug}"

        # Resolve host pakai DNS custom
        hostname = self.url.replace("https://", "").replace("http://", "")
        ip = self.resolve_with_custom_dns(hostname)
        print(f"[INFO] Resolving {hostname} via {self.dns} => {ip}")

        # Ganti host ke IP, tapi tetap kasih Host header agar HTTPS tidak error
        r = self.get(url, headers={"Host": hostname, **self.headers}, **kwargs)

        self.history_url = url
        return r.text

    def get_parsed_html(self, url, **kwargs):
        return BeautifulSoup(self.__get_html(url, **kwargs), "html.parser")

    def parsing(self, data):
        return BeautifulSoup(data, "html.parser")
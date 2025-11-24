from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) Mobile Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def convert_cookies(cookie_string):
    cookies = {}
    for part in cookie_string.split(";"):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            cookies[key] = value
    return cookies


def extract_groups(html):
    soup = BeautifulSoup(html, "html.parser")
    groups = []

    for a in soup.find_all("a"):
        href = a.get("href", "")

        if "/groups/" not in href:
            continue

        try:
            uid = href.split("/groups/")[1].split("/")[0].split("?")[0]

            if not uid.isdigit():
                continue

            name = a.text.strip()
            if name == "":
                continue

            groups.append({"uid": uid, "name": name})
        except:
            pass

    return groups


@app.route("/", methods=["GET", "POST"])
def home():
    groups = []
    error = None

    if request.method == "POST":
        cookie_input = request.form.get("cookies")

        if not cookie_input:
            return render_template("index.html", groups=groups, error="Please enter cookies.")

        cookies = convert_cookies(cookie_input)

        urls = [
            "https://mbasic.facebook.com/groups/?seemore",
            "https://mbasic.facebook.com/groups_browse/",
            "https://mbasic.facebook.com/groups/?ref=bookmarks"
        ]

        for url in urls:
            try:
                r = requests.get(url, cookies=cookies, headers=headers, timeout=8)

                if "login" in r.url:
                    error = "Invalid or expired cookies. Please login again and copy fresh cookies."
                    return render_template("index.html", groups=groups, error=error)

                extracted = extract_groups(r.text)

                if extracted:
                    groups.extend(extracted)

            except:
                pass

        if not groups:
            error = "No groups found. Your cookies might be invalid or Facebook layout changed."

    return render_template("index.html", groups=groups, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

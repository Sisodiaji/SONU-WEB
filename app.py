from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {"User-Agent": "Mozilla/5.0"}

def convert_cookies(cookie_string):
    cookies = {}
    for part in cookie_string.split(";"):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            cookies[key] = value
    return cookies

@app.route("/", methods=["GET", "POST"])
def home():
    group_list = []

    if request.method == "POST":
        cookie_text = request.form.get("cookies")
        cookies = convert_cookies(cookie_text)

        try:
            r = requests.get("https://mbasic.facebook.com/groups/?seemore",
                             cookies=cookies, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")

            for link in soup.find_all("a"):
                href = link.get("href", "")
                if "/groups/" in href and "?refid" in href:
                    try:
                        group_uid = href.split("/groups/")[1].split("?")[0]
                        group_name = link.text.strip()
                        group_list.append({"uid": group_uid, "name": group_name})
                    except:
                        pass
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html", groups=group_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

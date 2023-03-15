import requests
from bs4 import BeautifulSoup
import datetime
import openai
import tkinter as tk
from tkinter import ttk
import sys
from ttkthemes import ThemedTk, ThemedStyle
from tkinter import font
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('openai', 'api_key')

class NewsSummarizer:
    def __init__(self, api_key=None):
        if api_key is not None:
            openai.api_key = api_key
        self.base_url = "https://www.theregister.com/Archive/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    def summarize_text(self, text):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Please summarize the following text:\n\n{text}\n\nSummary:",
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()

    def fetch_articles(self, time_period):
        today = datetime.datetime.today()

        if time_period == "Today":
            dates = [today]
        elif time_period == "Past week":
            dates = [today - datetime.timedelta(days=x) for x in range(7)]
        else:
            dates = [today - datetime.timedelta(days=x) for x in range(30)]

        urls = [self.base_url + date.strftime("%Y/%m/%d") + "/" for date in dates]
        articles = []

        for url in urls:
            page = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(page.content, "html.parser")
            articles += soup.find_all("article")

        return articles

    def fetch_article_text(self, article_url):
        article_page = requests.get(article_url, headers=self.headers)
        article_soup = BeautifulSoup(article_page.content, "html.parser")
        article_text = "".join([p.get_text() for p in article_soup.find_all("p")])
        title = article_soup.title.string
        return title, article_text

class NewsSummarizerGUI:
    def __init__(self, summarizer):
        self.summarizer = summarizer
        self.root = ThemedTk(theme="breeze")
        self.root.title("News Article Summarizer")
        self.root.geometry("700x800")
        self.create_widgets()
        self.filtered_articles = []  # Add this line


    def create_widgets(self):
        # Add font
        style = ttk.Style(self.root)
        style.configure("TLabel", font=("Times New Roman", 12))
        style.configure("TCombobox", font=("Times New Roman", 12))
        style.configure("TButton", font=("Times New Roman", 12))

        self.time_period_label = ttk.Label(self.root, text="Select a time period:")
        self.time_period_label.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.time_period_var = tk.StringVar()
        self.time_period_dropdown = ttk.Combobox(self.root, textvariable=self.time_period_var, state="readonly")
        self.time_period_dropdown["values"] = ("Today", "Past week", "Past month")
        self.time_period_dropdown.current(0)
        self.time_period_dropdown.grid(column=1, row=0, padx=10, pady=10)

        self.fetch_button = ttk.Button(self.root, text="Fetch Articles", command=self.fetch_articles)
        self.fetch_button.grid(column=2, row=0, padx=10, pady=10)

        # Add the tag filter label and dropdown
        self.tag_filter_label = ttk.Label(self.root, text="Filter by tag:")
        self.tag_filter_label.grid(column=0, row=1, sticky=tk.W, padx=10, pady=10)

        self.tag_filter_var = tk.StringVar()
        self.tag_filter_dropdown = ttk.Combobox(self.root, textvariable=self.tag_filter_var, state="readonly")
        self.tag_filter_dropdown.grid(column=1, row=1, padx=10, pady=10)
        self.tag_filter_dropdown.bind("<<ComboboxSelected>>", self.filter_articles)

        self.articles_listbox = tk.Listbox(self.root, width=100, height=20, selectmode=tk.MULTIPLE, font=("Times New Roman", 12))
        self.articles_listbox.grid(column=0, row=2, columnspan=3, padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.articles_listbox.yview)
        self.scrollbar.grid(column=3, row=2, sticky=tk.N + tk.S, pady=10)
        self.articles_listbox["yscrollcommand"] = self.scrollbar.set

        self.summarize_button = ttk.Button(self.root, text="Summarize Article", command=self.summarize_article)
        self.summarize_button.grid(column=0, row=3, sticky=tk.W, padx=10, pady=10)

        self.summary_text = tk.Text(self.root, wrap=tk.WORD, width=100, height=20, font=("Times New Roman", 12))
        self.summary_text.grid(column=0, row=5, columnspan=3, padx=10, pady=10)

        self.api_key_label = ttk.Label(self.root, text="Update API Key:")
        self.api_key_label.grid(column=0, row=6, sticky=tk.W, padx=10, pady=10)

        self.api_key_entry = ttk.Entry(self.root, width=50)
        self.api_key_entry.grid(column=1, row=6, padx=10, pady=10)

        self.update_api_key_button = ttk.Button(self.root, text="Update API Key", command=self.update_api_key)
        self.update_api_key_button.grid(column=2, row=6, padx=10, pady=10)


    def fetch_articles(self):
        time_period = self.time_period_var.get()
        articles = self.summarizer.fetch_articles(time_period)
        self.articles = articles
        self.filtered_articles = articles  # Add this line
        self.articles_listbox.delete(0, tk.END)

        # Extract all unique tags and update the tag filter dropdown
        tags = sorted(set(article.find("span", {"class": "section_name"}).get_text() for article in articles))
        self.tag_filter_dropdown["values"] = ["All"] + tags
        self.tag_filter_dropdown.current(0)

        for article in articles:
            title = article.find("h4").get_text()
            self.articles_listbox.insert(tk.END, title)


    def filter_articles(self, event=None):
        selected_tag = self.tag_filter_var.get()
        self.articles_listbox.delete(0, tk.END)
        self.filtered_articles = []

        for article in self.articles:
            title = article.find("h4").get_text()
            tag = article.find("span", {"class": "section_name"}).get_text()

            if selected_tag == "All" or selected_tag == tag:
                self.articles_listbox.insert(tk.END, title)
                self.filtered_articles.append(article)

    def summarize_article(self):
        selected_indices = self.articles_listbox.curselection()
        summaries = []

        if not hasattr(self, "filtered_articles"):
            return

        for index in selected_indices:
            selected_article = self.filtered_articles[index]
            link = "https://www.theregister.com" + selected_article.find("a")["href"]
            title, article_text = self.summarizer.fetch_article_text(link)
            summary = self.summarizer.summarize_text(article_text)
            summaries.append(f"Title: {title}\n\nSummary: {summary}\n\n")

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "\n\n".join(summaries))



    def update_api_key(self):
        new_api_key = self.api_key_entry.get()
        config.set('openai', 'api_key', new_api_key)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        self.summarizer = NewsSummarizer(new_api_key)
        self.api_key_entry.delete(0, tk.END)


    def run(self):
        self.root.mainloop()


def main():
    news_summarizer = NewsSummarizer(api_key)
    gui = NewsSummarizerGUI(news_summarizer)
    gui.run()


if __name__ == "__main__":
    main()

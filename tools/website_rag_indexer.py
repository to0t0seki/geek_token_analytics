#  必要なライブラリのインポート
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import json
import hashlib
import time
import random




def url_to_safe_filename(url):
    # URLをハッシュ化して一意のファイル名を生成
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest() + '.html'

# ファイル名とURLのペアを保存するリスト
fnames = []
urls = []

# スクレイピング対象のURLリスト
with open('data/default_urls.json', 'r', encoding='utf-8') as f:
    urls.extend(json.load(f))
with open('data/urls.json', 'r', encoding='utf-8') as f:
    urls.extend(json.load(f))

# WebページにアクセスしてHTMLデータをローカルに保存
for url in urls:
    # URLを安全なファイル名に変換
    safe_fname = url_to_safe_filename(url)
    fname = f"data/raw_html_pages/{safe_fname}"
    fnames.append((fname, url))  # ファイル名とURLのタプルを保存
    response = requests.get(url)
    with open(fname, mode='w', encoding='utf-8') as fout:
        fout.write(response.text)
    time.sleep(random.uniform(0.5, 1.0))
    

# チャンクを分割するための設定
text_splitter = CharacterTextSplitter(
    separator='\n\n',  # 改行で分割
    chunk_size=500,  # 各チャンクのサイズ
    chunk_overlap=125,  # チャンク間の重複なし
    length_function=len  # 文字数でチャンクを計測
)

# 全てのチャンクを保持するリスト
all_chunks = []

# テキストを取得してチャンクに分割し、メタデータにURLを含める
for fname, url in fnames:
    with open(fname, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator="\n")

    # 抽出したテキストをチャンクに分割
    chunks = text_splitter.split_text(text)

    # 各チャンクをDocumentオブジェクトに変換してリストに追加
    for i, chunk in enumerate(chunks):
        # メタデータにURLを保存
        doc = Document(page_content=chunk, metadata={"source_url": url, "chunk_index": i})
        all_chunks.append(doc)

    print(f"Processed {fname}, {len(chunks)} chunks extracted.")

# OpenAPIに対応したベクトル変換を実施
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-3-small"
)

# ベクトルストアにチャンクを保存
db = FAISS.from_documents(all_chunks, embeddings)
db.save_local('../data/faiss_store')

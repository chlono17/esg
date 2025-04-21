import requests
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import messagebox
import os

# ✅ 你的 Finhub API Key
API_KEY = "d02rd9pr01qi6jgisdb0d02rd9pr01qi6jgisdbg"

def fetch_esg_data(symbol):
    """從 Finhub API 擷取 ESG 數據"""
    url = f"https://finnhub.io/api/v1/esg?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)

    print(f"🔍 擷取公司代碼：{symbol}")
    print("🔗 API 狀態碼：", response.status_code)
    print("🧾 回應內容：", response.text[:100], "...")  # 顯示前 100 字元即可

    if response.status_code != 200:
        raise Exception(f"API 錯誤：{response.status_code} - {response.text}")
    try:
        data = response.json()
    except Exception as e:
        raise Exception(f"JSON 解析錯誤：{e}\n原始內容：{response.text}")
    
    if not data:
        raise Exception("⚠️ 沒有 ESG 數據，請確認公司代碼正確")

    return pd.DataFrame([data])

def save_to_database(data, db_path, table_name):
    """將資料儲存至 SQLite"""
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_path)
    data.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def run_integration(symbol, db_path, table_name):
    try:
        abs_db_path = os.path.abspath(db_path)
        print(f"💾 儲存資料庫：{abs_db_path}")

        esg_data = fetch_esg_data(symbol)
        print(f"📊 抓到資料：\n{esg_data}")

        save_to_database(esg_data, abs_db_path, table_name)
        messagebox.showinfo("成功", f"{symbol} ESG 資料已存入：\n{abs_db_path}")
    except Exception as e:
        messagebox.showerror("處理失敗", str(e))

# === 建立 GUI ===

root = tk.Tk()
root.title("ESG 整合工具 v2")

# 股票代碼輸入
tk.Label(root, text="股票代碼（如 AAPL）：").grid(row=0, column=0, padx=10, pady=5, sticky="e")
symbol_entry = tk.Entry(root, width=30)
symbol_entry.insert(0, "AAPL")
symbol_entry.grid(row=0, column=1, padx=10, pady=5)

# 數據庫檔案名稱
tk.Label(root, text="數據庫檔案名稱：").grid(row=1, column=0, padx=10, pady=5, sticky="e")
db_entry = tk.Entry(root, width=30)
db_entry.insert(0, "esg_database.db")  # 可改為 "data/esg.db" 儲存在 data 資料夾
db_entry.grid(row=1, column=1, padx=10, pady=5)

# 表格名稱
tk.Label(root, text="資料表名稱：").grid(row=2, column=0, padx=10, pady=5, sticky="e")
table_entry = tk.Entry(root, width=30)
table_entry.insert(0, "esg_data")
table_entry.grid(row=2, column=1, padx=10, pady=5)

# 執行按鈕
start_button = tk.Button(root, text="開始整合", command=lambda: run_integration(
    symbol_entry.get(), db_entry.get(), table_entry.get()
))
start_button.grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # for headless use
import matplotlib.pyplot as plt
import seaborn as sns

class SalesAnalyzer:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, low_memory=False)
        self.kpis = {}
        self.standardize_columns()

    def standardize_columns(self):
        def norm(c):
            c = str(c).strip().lower().replace(" ", "_")
            c = c.replace("(", "").replace(")", "").replace("-", "_")
            return c
        self.df.columns = [norm(c) for c in self.df.columns]

    def find_col(self, candidates):
        for cand in candidates:
            if cand in self.df.columns:
                return cand
        for cand in candidates:
            for c in self.df.columns:
                if cand in c:
                    return c
        return None

    def convert_dates(self):
        col = self.find_col(["order_date", "date", "orderdate"])
        if col:
            try:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
            except:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce", dayfirst=True)
            if col != "order_date":
                self.df.rename(columns={col: "order_date"}, inplace=True)

    def convert_numerics(self):
        def clean(col):
            self.df[col] = (
                self.df[col].astype(str)
                .str.replace(r"[^0-9\.\-]", "", regex=True)
                .replace("", np.nan)
                .astype(float)
            )

        qty = self.find_col(["quantity", "qty"])
        price = self.find_col(["unit_price", "price"])
        sales = self.find_col(["sales", "amount", "total"])
        profit = self.find_col(["profit"])

        for col in [qty, price, sales, profit]:
            if col:
                clean(col)

        if sales and sales != "sales":
            self.df.rename(columns={sales: "sales"}, inplace=True)

        if qty and qty != "quantity":
            self.df.rename(columns={qty: "quantity"}, inplace=True)

        if price and price != "unit_price":
            self.df.rename(columns={price: "unit_price"}, inplace=True)

        if profit and profit != "profit":
            self.df.rename(columns={profit: "profit"}, inplace=True)

        if "sales" not in self.df.columns and "quantity" in self.df.columns and "unit_price" in self.df.columns:
            self.df["sales"] = self.df["quantity"] * self.df["unit_price"]

    def clean_data(self):
        self.convert_dates()
        self.convert_numerics()
        self.df.drop_duplicates(inplace=True)
        self.df.fillna(0, inplace=True)

    def compute_kpis(self):
        k = {}
        k["total_revenue"] = self.df["sales"].sum()
        k["total_profit"] = self.df["profit"].sum() if "profit" in self.df.columns else np.nan
        k["avg_order_value"] = k["total_revenue"] / len(self.df)
        k["profit_margin_pct"] = 100 * (k["total_profit"] / k["total_revenue"]) if k["total_revenue"] else np.nan
        k["avg_units_per_order"] = self.df["quantity"].mean() if "quantity" in self.df.columns else np.nan
        self.kpis = k
        return k

    def monthly_revenue(self):
        if "order_date" not in self.df.columns:
            return pd.Series()
        tmp = self.df.copy()
        tmp["month"] = tmp["order_date"].dt.to_period("M").dt.to_timestamp()
        return tmp.groupby("month")["sales"].sum()

    def region_sales(self):
        region_col = self.find_col(["region", "state"])
        if not region_col:
            return pd.Series()
        return self.df.groupby(region_col)["sales"].sum().sort_values(ascending=False)

    def plot_monthly_revenue(self, outpath):
        mr = self.monthly_revenue()
        if mr.empty:
            return
        plt.figure()
        sns.lineplot(x=mr.index, y=mr.values, marker="o")
        plt.title("Monthly Revenue")
        plt.savefig(outpath, bbox_inches="tight")
        plt.close()

    def plot_region_sales(self, outpath):
        rs = self.region_sales()
        if rs.empty:
            return
        plt.figure()
        sns.barplot(x=rs.values, y=rs.index)
        plt.title("Region-wise Revenue")
        plt.savefig(outpath, bbox_inches="tight")
        plt.close()

    def run_all(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        self.clean_data()
        self.compute_kpis()
        cleaned = os.path.join(outdir, "cleaned_sales.csv")
        self.df.to_csv(cleaned, index=False)
        self.plot_monthly_revenue(os.path.join(outdir, "monthly_revenue.png"))
        self.plot_region_sales(os.path.join(outdir, "region_revenue.png"))
        return cleaned

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sales_analyzer_script.py input.csv output_folder")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_dir = sys.argv[2]

    an = SalesAnalyzer(input_csv)
    an.run_all(output_dir)
    print("Done. Output folder:", output_dir)

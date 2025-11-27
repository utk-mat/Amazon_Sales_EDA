
Assignment: eRetail Sales Data Cleaning & Exploratory Analysis
Submitted by: Utkarsh Mathur

Files included:
1) cleaned_amazon_sales.csv         - cleaned dataset used for analysis
2) sales_analyzer_script.py         - runnable script to reproduce results
3) monthly_revenue.png              - plot of monthly revenue
4) region_revenue.png               - top regions by revenue
5) sales_scatter.png                - sales over time scatter plot
6) assignment_submission.zip        - zip with all above files
7) Amazon_Sales_EDA.ipynb           - original Jupyter notebook (include when submitting)
8) README.txt                       - this file

How to run (locally):
- Open the notebook and run all cells, OR:
- From terminal:
    python sales_analyzer_script.py "/path/to/Amazon Sale Report(in).csv" "/path/to/output_dir"

Screenshots to include in submission:
- Cleaned data preview: first 8 rows after cleaning (cell output)
- KPIs printed (cell output)
- Each plot (png files above)

Notes:
- I standardized column names to lowercase and underscores.
- If the date column didn't parse correctly, I attempted both month-first and day-first formats.
- If any expected columns (sales, quantity, profit) are missing, the script attempts to compute sales from quantity * unit_price when possible.


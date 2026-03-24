import pandas as pd

# Load data
df = pd.read_csv('cleaned_data.csv')

# 1. Success Rate
success_rate = (df['deal'].sum() / len(df)) * 100

# 2. Industry Analysis
industry_counts = df['industry'].value_counts()

# 3. Average Valuation Gap
df['val_gap'] = df['ask_valuation'] - df['deal_valuation']
avg_gap = df['val_gap'].mean()

print(f"Total Success Rate: {success_rate:.2f}%")
print("Top Industries:\n", industry_counts)
print(f"Average Valuation Haircut: {avg_gap:.2f} Lakhs")
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Constants
DATA_FILE = 'gold_data.csv'

# Load Data
def load_data():
    """Load data from CSV file or create default data."""
    return pd.read_csv(DATA_FILE)

# Save Data
def save_data(df):
    """Save data to CSV file."""
    df.to_csv(DATA_FILE, index=False)

# Streamlit Interface
st.title("Gold Purchase and Sale Management")
st.sidebar.title("🪙 Gold Data 🪙")

# Load or initialize data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Layout with two columns
col1, col2 = st.columns(2)

# Sidebar Options
with st.sidebar.expander("**Add Purchase**"):
    purchased_date = st.date_input('Purchased Date')
    chf_per_gram = st.number_input('CHF Per Gram', format="%.2f")
    quantity_purchased = st.number_input('Quantity Purchased', format="%.2f")
    cost = chf_per_gram * quantity_purchased
    st.text_input('Cost', value=f'{cost:.2f}', disabled=True)

    if st.button('Add Purchase'):
        new_data = {
            "Purchased_Date": [purchased_date],
            "Gram_Per_CHF": [chf_per_gram],
            "Quantity_Purchased": [quantity_purchased],
            "Cost": [cost],
            "Type": ["Purchase"]
        }
        new_df = pd.DataFrame(new_data)
        st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
        save_data(st.session_state.df)
        st.success('Purchase added successfully!')

with st.sidebar.expander("**Sell Gold**"):
    sell_date = st.date_input('Sale Date')
    sell_gram_per_chf = st.number_input('Sale Gram Per CHF', format="%.2f")
    sell_quantity = st.number_input('Sale Quantity', format="%.2f")
    sell_cost = sell_gram_per_chf * sell_quantity
    st.text_input('Sale Cost', value=f'{sell_cost:.2f}', disabled=True)

    if st.button('Add Sale'):
        sale_data = {
            "Purchased_Date": [sell_date],
            "Gram_Per_CHF": [sell_gram_per_chf],
            "Quantity_Purchased": [sell_quantity],
            "Cost": [sell_cost],
            "Type": ["Sale"]
        }
        sale_df = pd.DataFrame(sale_data)
        st.session_state.df = pd.concat([st.session_state.df, sale_df], ignore_index=True)
        save_data(st.session_state.df)
        st.success('Sale added successfully!')

with st.sidebar.expander("**Delete Row**"):
    if not st.session_state.df.empty:
        index_to_delete = st.number_input("Enter the index of the row to delete", min_value=0,
                                          max_value=len(st.session_state.df) - 1)

        if st.button('Delete Row'):
            if index_to_delete in st.session_state.df.index:
                st.session_state.df = st.session_state.df.drop(index_to_delete).reset_index(drop=True)
                save_data(st.session_state.df)
                st.success('Row deleted successfully!')
            else:
                st.error("Entered index does not exist!")
    else:
        st.write("No data to delete.")

with st.sidebar.expander("**Current CHF per Gram**"):
    current_gram_price_in_chf = st.number_input('Enter Current CHF per Gram', format="%.2f")

with st.sidebar.expander("**Net Profit per Gram in CHF**"):
    net_profit = st.number_input('Enter Net Profit per Gram in CHF', format="%.2f")

# Main Page Content
with col1:
    st.header('Current Data')

    def highlight_row(row):
        return ['color: red' if row['Type'] == 'Sale' else 'color: green'] * len(row)

    df = st.session_state.df
    styled_df = df.style.apply(highlight_row, axis=1)
    st.dataframe(styled_df)

with col2:
    st.header('Statistics')

    purchases = df[df['Type'] == 'Purchase']
    sales = df[df['Type'] == 'Sale']

    total_gold_quantity_in_gram = purchases['Quantity_Purchased'].sum()
    total_money_spent_in_chf = purchases['Cost'].sum()
    average_gram_price_in_chf = total_money_spent_in_chf / total_gold_quantity_in_gram if total_gold_quantity_in_gram != 0 else 0
    total_money_after_sold = sales['Cost'].sum()
    net_profit_per_gram_in_chf = current_gram_price_in_chf - average_gram_price_in_chf if total_gold_quantity_in_gram != 0 else 0
    total_profit_in_chf = total_gold_quantity_in_gram * net_profit_per_gram_in_chf

    decision = 'SELL' if net_profit_per_gram_in_chf > net_profit else 'KEEP'

    dict_data = {
        'Outputs': [
            'Total Gold Quantity in Gram',
            'Total Money Spent in CHF',
            'Average Gram Price in CHF',
            'Current Gram Price in CHF',
            'Net Profit Per Gram in CHF',
            'Total Profit in CHF',
            'Total Money After Sold in CHF',
            'Decision'
        ],
        'Values Regarding Gold': [
            total_gold_quantity_in_gram,
            total_money_spent_in_chf,
            round(average_gram_price_in_chf, 4),
            current_gram_price_in_chf,
            round(net_profit_per_gram_in_chf, 4),
            round(total_profit_in_chf, 4),
            round(total_money_after_sold, 4),
            decision
        ]
    }
    df_dict_data = pd.DataFrame(dict_data)
    st.write(df_dict_data)

# Plotting Graphs
with col2:
    st.header('Gold Metrics Over Time')

    df_sorted = df.sort_values(by='Purchased_Date')

    sns.set_style('darkgrid')

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_sorted, x='Purchased_Date', y='Gram_Per_CHF', label='Gram Per CHF', marker='o', markersize=15, linestyle='--', ax=ax, color='blue')
    ax.set_title('Gold Metrics Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('CHF Per Gram')
    ax.legend()
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_sorted, x='Purchased_Date', y='Quantity_Purchased', label='Quantity Purchased', marker='o', markersize=15, linestyle='--', ax=ax, color='green')
    ax.set_title('Gold Metrics Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Quantity Purchased')
    ax.legend()
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_sorted, x='Purchased_Date', y='Cost', label='Cost', marker='o', markersize=15, linestyle='--', ax=ax, color='red')
    ax.set_title('Gold Metrics Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cost')
    ax.legend()
    st.pyplot(fig)

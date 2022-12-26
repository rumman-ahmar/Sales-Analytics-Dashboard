import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Analytics Dashboard | Rumman Ahmar",
                   page_icon=":bar_chart:", layout="wide")

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---- READ EXCEL ----
# @st.cache
def get_data_from_excel():
    df = pd.read_csv('supermarket_sales.csv')
    df.drop(columns='Row ID', inplace=True)
    df.rename(columns={'Ship Mode': "Ship_Mode"}, inplace=True)
    df["Postal Code"].fillna(5401.0, inplace=True)
    df["Order Date"] = pd.to_datetime(df["Order Date"], format='%d/%m/%Y')
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format='%d/%m/%Y')
    # creating the columns 'Year' and 'Month'
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.strftime('%b')
    df['Month'] = pd.Categorical(df['Month'],
                                 categories=months, ordered=True)
    return df


df = get_data_from_excel()
query_string = ""

# # ---- SIDEBAR ----
st.sidebar.header("Filters:")
order_year = st.sidebar.multiselect(
    "Select order year:", options=df["Year"]
    .unique()
)
if order_year:
    query_string += "& Year == @order_year"

category = st.sidebar.multiselect(
    "Select category:", options=df["Category"]
    .unique()
)
if category:
    query_string += "& Category == @category"

region = st.sidebar.multiselect(
    "Select region:", options=df["Region"]
    .unique()
)
if region:
    query_string += "& Region == @region"

state = st.sidebar.multiselect(
    "Select state:", options=df["State"]
    .unique()
)
if state:
    query_string += "& State == @state"

ship_mode = st.sidebar.multiselect(
    "Select ship mode:", options=df["Ship_Mode"]
    .unique()
)
if ship_mode:
    query_string += "& Ship_Mode == @ship_mode"


# ---- QUERY ----
if query_string:
    if query_string[0] == "&":
        query_string = query_string[1:]
    df = df.query(query_string)


# ---- MAINPAGE ----
st.title(":bar_chart: Sales Analytics Dashboard")
st.markdown("##")

# # TOP KPI's
total_sales = int(df["Sales"].sum())
average_sale_by_transaction = round(df["Sales"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Most Ordered City:")
    st.subheader(df['City'].value_counts().idxmax())
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("""---""")
# SALES BY YEAR [LINE CHART]
sales_by_year = df.groupby(by=["Year"], sort=True).sum()[["Sales"]]
fig_year_sales = px.line(
    sales_by_year,
    x=sales_by_year.index,
    y="Sales",
    title="<b>Sales by Year</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_year),
    template="plotly_white",
)
fig_year_sales.update_layout(
    xaxis=dict(tickmode="linear", showgrid=False),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# SALES BY MONTH [BAR CHART]
sales_by_month = df.groupby(by=["Month"], sort=False).sum()[["Sales"]]
fig_monthly_sales = px.bar(
    sales_by_month,
    x=sales_by_month.index,
    y="Sales",
    title="<b>Sales by Month</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_month),
    template="plotly_white",
)
fig_monthly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)
left_column, right_column = st.columns(2)
if not order_year or len(order_year) > 1:
    left_column.plotly_chart(fig_year_sales, use_container_width=True)
else:
    left_column.warning('Sales by year can be seen only if more than \
        year selected from filters')
right_column.plotly_chart(fig_monthly_sales, use_container_width=True)


# SALES BY BEST PRODUCT [BAR CHART]
best_prod = df.groupby("Product Name")["Sales"].sum()\
    .reset_index().sort_values("Sales", ascending=False).head(10)

fig_best_prod = px.bar(
    best_prod,
    x="Sales",
    y=best_prod['Product Name'],
    orientation="h",
    title="<b>Top 10 Best Selling Products</b>",
    color_discrete_sequence=["#0083B8"] * len(best_prod),
    template="plotly_white",
)
fig_best_prod.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    yaxis=dict(autorange="reversed")
)

category_dist = df.groupby("Category")["Sales"].sum()\
    .reset_index().sort_values("Sales", ascending=False)
fig_category_dist = px.pie(category_dist, values='Sales',
                           names="Category",
                           title='<b>Category Sales Distribution<b>')

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_category_dist, use_container_width=True)
right_column.plotly_chart(fig_best_prod, use_container_width=True)

st.markdown("""---""")
most_valuable_customers = df.groupby("Customer Name")["Sales"]\
    .sum().sort_values(ascending=False).head(10)
fig_most_valuable_customers = px.bar(
    most_valuable_customers,
    x=most_valuable_customers.index,
    y="Sales",
    title="<b>Top 10 Most Valuable Customers</b>",
    color_discrete_sequence=["#0083B8"] * len(most_valuable_customers),
    template="plotly_white",
)
fig_most_valuable_customers.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


region_sale = df.groupby("Region")["Sales"]\
    .sum().sort_values(ascending=False).head(10)
fig_region_sale = px.bar(
    region_sale,
    x=region_sale.index,
    y="Sales",
    title="<b>Top Regions</b>",
    color_discrete_sequence=["#0083B8"] * len(region_sale),
    template="plotly_white",
)
fig_region_sale.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_most_valuable_customers, use_container_width=True)
right_column.plotly_chart(fig_region_sale, use_container_width=True)

st.markdown("""---""")
st.subheader("Sales Data")
st.dataframe(df)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

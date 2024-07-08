import numpy as np
import pandas as pd
from flask import Flask, render_template 

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def homePage():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)

    """

# Convert to dataframe
df = pd.DataFrame(pd.read_excel("CorporateActionsData.xlsx", engine='openpyxl'))

# Cleaning for any duplicate IDs
df.drop_duplicates(subset=["key_corporateActionId"], inplace=True)

# Cleaning for any blanks 
for col in df.columns:
    df.dropna(subset=[col], inplace=True)

# Store country for each currency to convert
countryHashmap = {
    "GBP":"United Kingdom",
    "KRW":"South Korea",
    "EUR":"Europe",
    "INR":"India",
    "CNY":"China",
    "NOK":"Norway",
    "USD":"United States",
    "THB":"Thailand",
    "CAD":"Canada"
}

# Store currency ratio to convert to GBP for normalisation 
currencyRatioHashmap = {
    "KRW":0.00056417541,
    "EUR":0.85,
    "INR":0.0093,
    "CNY":0.11,
    "NOK":0.074,
    "USD":0.78,
    "THB":0.021,
    "CAD":0.57
}

# Create column to store country of origin 
df["countryOrigin"] = None

# Convert transactions to GBP for consistency
def convertRowsToPounds(row):
    # Get relevant data
    transactionAmount = row.iat[4]
    transactionCurrency = row.iat[5]

    # If not the current we're converting to, then create new conversion and change transaction amount
    if transactionCurrency != "GBP":
        newAmount = round(transactionAmount * currencyRatioHashmap[transactionCurrency], 2)
        row.iat[4] = newAmount

    # Update country
    row.iat[6] = countryHashmap[transactionCurrency]

    return row
df = df.apply(convertRowsToPounds, axis="columns")
# New column names for simplicity
# print(df.columns)
df.columns = ["corpActionID", "declaredDate", "infoSource","dealAttributes","transactionAmount","transactionCurrency","countryOrigin"]

# Return clean excel file 
df.to_excel("result.xlsx", index=False)"""
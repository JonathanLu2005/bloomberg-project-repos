import numpy as np
import pandas as pd

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

def initialiseDataFrame(file_name):
    # Convert to dataframe
    df = pd.DataFrame(pd.read_excel(file_name, engine='openpyxl'))

    # Cleaning for any duplicate IDs
    df.drop_duplicates(subset=["key_corporateActionId"], inplace=True)

    # Cleaning for any blanks 
    for col in df.columns:
        df.dropna(subset=[col], inplace=True)

    # Create column to store country of origin 
    df["geographicalRegion"] = None

    df = df.apply(convertRowsToPounds, axis="columns")
    # New column names for simplicity
    # print(df.columns)
    df.columns = ["corpActionID", "declaredDate", "infoSource","dealAttributes","transactionAmount","transactionCurrency","geographicalRegion"]

    # Return clean excel file 
    df.to_excel("uploads/result.xlsx", index=False)
    
    return df

# Determine the number of transactions in each country
# Determine total transaction value from each country (possibly in the same graph)
def analyseData(df, group_criterion, column_headings):
    # group_criterion can be either countryOrigin or declaredDate for geographic or time-based groupings respectively
    
    # The first entry in column_headings is used as the name for the indices the remaining entries are name for the dataframe columns

    group = df.groupby(group_criterion)
    num_transactions = group.size()
    avg_transactions = group.transactionAmount.mean()
    std_transactions = group.transactionAmount.std()
    min_transaction = group.transactionAmount.min()
    max_transaction = group.transactionAmount.max()

    df = pd.DataFrame({"0":num_transactions , "1":avg_transactions, "2":std_transactions, "3":min_transaction, "4":max_transaction})
    df.rename_axis(column_headings[0], inplace=True)
    df.columns = column_headings[1:]
    return df.values    # Returns a 2d array containing the content of the table

# Use case sample below
if __name__ == "__main__":
    df = initialiseDataFrame("CorporateActionsData.xlsx")
    geo_df = analyseData(df, "countryOrigin", ["Geographical Region", "Transaction Count",\
        "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"])
    print(geo_df)
    print(type(geo_df.values))

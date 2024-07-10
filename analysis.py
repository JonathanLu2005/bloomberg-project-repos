import numpy as np
import pandas as pd
from calendar import month_name

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
    # transactionSum = lambda s:s.transactionAmount.sum()

    # Convert from a a full date, to just the number of the month of the year when analysing based on time
    if group_criterion == "declaredDate":
        df["declaredDate"] = df["declaredDate"].map(lambda d: int(d.split("-")[1])) # Convert each date to the month number
    
    if group_criterion == "dealAttributes":
        df = expandDealAttributes(df)
        # Expand the deal attributes to be handled separately
        
    group = df.groupby(group_criterion)
    num_transactions = group.size()
    avg_transactions = group.transactionAmount.mean()
    std_transactions = group.transactionAmount.std()
    min_transaction = group.transactionAmount.min()
    max_transaction = group.transactionAmount.max()

    df = pd.DataFrame({"0":num_transactions , "1":avg_transactions, "2":std_transactions, "3":min_transaction, "4":max_transaction})
    
    # Put the months in chronological order and convert the month number to its value e.g. 1=January, 2=February ...
    if group_criterion == "declaredDate":
        df.sort_index(inplace=True)
        df.index = df.index.map(lambda x: month_name[x])
    
    if group_criterion == "dealAttributes":
        df.index = df.index.map(lambda s: s.strip("\"").replace("_", " "))
        # Remove awkward initial formatting, for a more natural presentation in a table

    # Format all numbers to 2.d.p and replace Null std with 0
    df["1"] = df["1"].map(lambda x: "{:.2f}".format(round(x, 2)))
    df["2"] = df["2"].map(lambda x: "{:.2f}".format(round(x, 2)) if not pd.isnull(x) else "0.00") 
    df["4"] = df["4"].map(lambda x: "{:.2f}".format(round(x, 2)))

    df.columns = column_headings[1:]
    df.rename_axis("", inplace=True)
    df.rename_axis(column_headings[0], axis="columns", inplace=True) # Writes the name of the index column in the top-left corner
    
    return df

'''
cleanseDealAttributes()
Extracts each of the attributes to extend the data frame so that each attribute has its own row instead of a list
E.g. If a deal attribute entry contains the list ["COMPANY_TAKEOVER", "REVERSE_MERGER", "MINORITY_PURCHASE"]
then the code below will extract each individaul attribute from above into its own row
'''
def expandDealAttributes(df):
    deal_attributes_col = df.dealAttributes

    modified_df = pd.DataFrame(columns=df.columns)

    modified_index = 0
    for index, attributes in deal_attributes_col.items():
        attributes = attributes.strip("[]").split(",")
        temp = df.loc[index]
        for att in attributes:
            temp.dealAttributes = att
            modified_df.loc[modified_index] = temp
            modified_index += 1
    
    return modified_df

if __name__ == "__main__":
    df = initialiseDataFrame("CorporateActionsData.xlsx")
    _df = expandDealAttributes(df)
    deal_df = analyseData(_df, "dealAttributes", ["Deal Type", "Transaction Count",\
         "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"])
    print(deal_df)
    # print(_df.dealAttributes)
    # geo_df = analyseData(df, "geographicalRegion", ["Geographical Region", "Transaction Count",\
    #     "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"])
    # print(geo_df)
    # print(type(geo_df.values))
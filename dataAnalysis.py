# Import libraries
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

    # Convert the dataframe transaction to GBP
    df = df.apply(convertRowsToPounds, axis="columns")

    # New column names for simplicity
    df.columns = ["corpActionID", "declaredDate", "infoSource","dealAttributes","transactionAmount","transactionCurrency","geographicalRegion"]

    # Return clean excel file 
    df.to_excel("uploads/result.xlsx", index=False)
    
    # Return clean data frame to work with
    return df

# Analyse the data for each country, time and deal attribute
def analyseData(df, group_criterion, column_headings):
    # If we want to get the correlation of time, then convert each date to the month number
    if group_criterion == "declaredDate":
        df["declaredDate"] = df["declaredDate"].map(lambda d: int(d.split("-")[1]))
    
    # If we want to get deal attributes data, need to get each attribute
    if group_criterion == "dealAttributes":
        df = expandDealAttributes(df)
        
    # Put those groups of data to analyse (deal, time, country) to a group
    group = df.groupby(group_criterion)

    # Able find the following data with Pandas methods
    num_transactions = group.size()
    avg_transactions = group.transactionAmount.mean()
    std_transactions = group.transactionAmount.std()
    min_transaction = group.transactionAmount.min()
    max_transaction = group.transactionAmount.max()

    # New data frame for results
    df = pd.DataFrame({"0":num_transactions , "1":avg_transactions, "2":std_transactions, "3":min_transaction, "4":max_transaction})
    
    # Put the months in chronological order and convert the month number to its value e.g. 1=January, 2=February ...
    if group_criterion == "declaredDate":
        df.sort_index(inplace=True)
        df.index = df.index.map(lambda x: month_name[x])
    
    # Remove awkward initial formatting, for a more natural presentation in a table
    if group_criterion == "dealAttributes":
        df.index = df.index.map(lambda s: s.strip("\"").replace("_", " "))

    # Format all numbers to 2.d.p and replace Null std with 0
    df["1"] = df["1"].map(lambda x: "{:.2f}".format(round(x, 2)))
    df["2"] = df["2"].map(lambda x: "{:.2f}".format(round(x, 2)) if not pd.isnull(x) else "0.00") 
    df["4"] = df["4"].map(lambda x: "{:.2f}".format(round(x, 2)))

    # Writes the name of the index column in the top-left corner
    df.columns = column_headings[1:]
    df.rename_axis("", inplace=True)
    df.rename_axis(column_headings[0], axis="columns", inplace=True)
    
    # Return result of results
    return df

# Extract each of the attributes to extend the DF so each attribute has its own row instead of being an array
def expandDealAttributes(df):
    # Get deal attributes columns
    deal_attributes_col = df.dealAttributes

    # Empty DF to write changes but use existing DF column names
    modified_df = pd.DataFrame(columns=df.columns)

    # Track current row in new DF
    modified_index = 0
    for index, attributes in deal_attributes_col.items():
        # List of attributes from string to list
        attributes = attributes.strip("[]").split(",")

        # Current row of existing DF
        temp = df.loc[index]

        # New row in DF for each attribute
        for att in attributes:
            # Ensure rows are the deal attributes
            temp.dealAttributes = att

            # New row to data frame and append to next rows
            modified_df.loc[modified_index] = temp
            modified_index += 1
    
    # Return new DF
    return modified_df

if __name__ == "__main__":
    df = initialiseDataFrame("CorporateActionsData.xlsx")
    _df = expandDealAttributes(df)
    deal_df = analyseData(_df, "dealAttributes", ["Deal Type", "Transaction Count",\
         "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"])
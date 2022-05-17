# Stocks
----

Contains the following python script:
1. Stocks

**Summary**:
- Stocks: This script extracts output from an executable programme. It stores the output into multiple files, and reads each one individually, at a 10 second lag. To optimise the efficiency of extraction, multiprocessing is implemented. All the output on multiple financial stocks are collected.

**Skills**:
1. Familiarity with multiprocessing and threading capabilities to boost code efficiency.
2. Collecting output from executable programmes using pythons `subprocessor`.
3. Uploading the output into an SQL database.

Future Updates:
1. Machine learning models to forecast pricing estimates
2. Including a schedule to run the script for a fixed amount of time.


# Financial-Statistics (OLD)
----
The folder 'Financial' contains updated records of Bitcoin shares, and an R script of machine learning to calculate the probabilities of the 'next-minute' falling or increasing in difference between both Closed and Open stock shares. 

It's calculated via:

```
Open_Stock - Closed_stock
```

Then from these values, take the difference of the next minute relative to the last, and categorise these within ranges. Then take a machine learning model of time, open and closed stocks, to understand what's the probability of various ranges falling into one of these categories in the next minute.


# DLBDSDQDW01-Data-Quality-and-Data-Wrangling
Web scraping of four websites.
## Project Description
This project focuses on analyzing the housing market using web scraping techniques. It includes a web scraper, implemented as a Python script and an IPython Notebook (.ipynb) file for data analysis. The data collected from various websites is stored in the scraping_data.h5 file.
Motivation
The housing market plays a crucial role in the global economy, but it also raises social concerns due to increasing prices and potential exclusion of certain groups. Obtaining accurate and up-to-date data in this dynamic market is challenging for policymakers. Web scraping offers a solution by automatically collecting data from real estate platforms, providing valuable insights into current market trends.
## Data Collection
The web scraper extracts data from three websites:
1.	Immowelt.de: One of the leading real estate platforms in Germany and Austria, providing daily updated information about residential rental properties in Munich. Data includes rental prices, number of rooms, square meters, and location within the city.
2.	Börse.de: The website of the German stock exchange, offering current stock market information. The scraper retrieves the stock price and market capitalization of the four largest real estate stock corporations in Germany.
3.	Booking.com: A renowned digital travel company, offering hotel room booking services. The scraper collects hotel room rates in Munich for a specific period.
Data collection occurred over a one-week period, from May 23, 2023, to May 29, 2023.
## Limitations
While this study allows for hypothesis testing with the available dataset, it's important to note some limitations:
•	To obtain statistically robust results, data collection should be extended over a more extended period and cover a larger geographical area, potentially including the entire country.
•	The time frame and location (Munich) studied here may not capture broader market trends.
## Technical Approach
The project utilizes Python libraries such as Beautiful Soup and Selenium for web scraping. The code is designed to be reusable, with various functionalities encapsulated in functions. The scraper script retrieves data from each website and saves it in the appropriate format to the HDF5 file.
The HDF5 file structure consists of groups for each website, with daily data stored in subgroups categorized by date.
## Legal Considerations
The German Federal Court of Justice in 2014, stating that scraping is not automatically illegal, even if it violates a website's terms and conditions. The scraping of Yahoo Finance was not executed due to explicit prohibition, but alternative sources were used to gather stock market data.
## Conclusion
This scraper demonstrates a methodology for collecting data for various scientific inquiries. Additionally, it emphasizes the potential of web scraping to provide valuable insights in rapidly evolving fields such as the housing market.
For further details and analysis results, please refer to the IPython Notebook file "Analysis.ipynb" and the collected data in "scraping_data.h5".


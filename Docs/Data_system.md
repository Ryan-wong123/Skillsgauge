# Data System 
CSV | Parquet | Duck DB | R2

Medallion system for data storage (data lake)



currently JS scraper follow this 

**Bronze (CSV):**

scraper scrape weekly into CSV order by date it was scraped.
Contain the raw scrape data to be clean into silver level.




**Silver (Parquet):** 

Cleaning script clean the bronze dataset, merge and dedupe into silver parquet level to be stored in R2




**Gold (Parquet):** 

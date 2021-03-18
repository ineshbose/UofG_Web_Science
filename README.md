# UofG Web Science (H)

This repository has the coursework for Web Science (H).

## Introduction

The objective of this coursework is to develop a Twitter crawler for data collection in English and to conduct social media analytics. It is recommended to use Python language and also MongoDB for data storage.

The code and report needs to be submitted on or before the specified deadline. In addition, a sample of the data set collection should be provided.

The coursework will be marked out of 100 and will have 20% weight of the final marks. As the usual practice across the school, numerical marks will be appropriately converted into bands.

Tweets which are posted in United Kingdom are of main interest and need to be collected for 1 hour of any day. In addition, sample multimedia contents for tweets with media objects should be downloaded.

## Specific Tasks to Do

Develop a crawler to access as much Twitter data as possible and group the tweets based on similarity. Use important activity specific data to crawl additional data. During this process, Twitter data access APIs along with access constraints will be identified.

1. Use Twitter Streaming API for collecting data. Use Streaming API with a United Kingdom geographical filter along with selected words. Count the amount of data collected. Consider all the data collected for counting this, and count the re-tweets and quotes. [10 marks]

2. Group the tweets based on similarity - count the number of groups; count the elements in each group; identify prominent groups; prioritise terms in the group; identify entities in each group. Use this information to develop a REST API based crawler for activity specific data. [20 marks]
    1. Implement data structures to handle large stream of data. As the amount of data increases, better strategies may be needed to manage this. [10 marks]

3. Enhance the crawling using the hybrid architecture of Twitter Streaming & REST APIs. [20 marks]
    1. For example, topic-based or user-based streaming. This should be based on the identified groups and concepts.
    2. Provide Statistics - count the redundant data present in the collection; and redundancy can be counted using the Tweet ID.

4. Analyse geo-tagged data for the UK for the period. Count the amount of collected geo-tagged data from the UK. Measure if there is any overlap between REST and Streaming APIs. [10 marks]

5. Download multimedia contents including videos and pictures for tweets with media objects. Provide a basic analysis of collected data. [10 marks]

6. Discuss the data access strategies implemented. Clearly specify the Twitter API specific restrictions encountered and they were addressed for collecting as much Twitter data as possible.

## Report Structure

The report should be written with a 11pt font and with the maximum length of 10 pages. It should be organised the following way:

1. Section 1: Introduction
    1. Describe the software developed with appropriate details
    2. Specify the time and duration of data collected

2. Section 2: Data Crawl
    1. Use the Twitter Streaming API for collecting 1% data and specify the APIs used
    2. Describe the seed crawl data used and provide in tabular form data collected:
        | Total | Streaming API | Retweets | Quotes | Images | Verified Count | Geotagged Data Count | Location Count |
        | ----- | ------------- | -------- | ------ | ------ | -------------- | -------------------- | -------------- |
        |       |               |          |        |        |                |                      |                |
    3. Specify data grouping methods and associated statistics and provide data in tabular form:
        | Total | Groups | Min Size | Max Size | Avg Size | ... |
        | ----- | ------ | -------- | -------- | -------- | --- |
        |       |        |          |          |          |     |
    4. Discuss how issues with large amount of data and groups were addressed and what data structures were used. Discuss results in tabular form:
        | Total | Streaming API | REST API | Redundant | Quotes | Retweets | Geotagged Data Count | Media Count |
        | ----- | ------------- | -------- | --------- | ------ | -------- | -------------------- | ----------- |
        |       |               |          |           |        |          |                      |             |
    5. Discuss download strategies for tweets with media objects

3. Section 3: Scheduler/Ranker
    1. Describe the design of the scheduler to address Twitter access restrictions
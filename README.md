# 📊 YouTube Trending Video Analytics – US Dataset

---

## 📌 Project Overview

This project analyzes the US YouTube Trending dataset to uncover patterns in trending videos. The objective is to identify high-performing categories, analyze sentiment in video titles, measure engagement levels, and understand how quickly videos trend after publishing.

The project combines data cleaning, sentiment analysis, SQL-based aggregation, and dashboard visualization to derive meaningful insights from the dataset.

---

## 🎯 Objectives

* Identify top-performing video categories
* Analyze title sentiment (Positive, Negative, Neutral)
* Measure engagement rate beyond views
* Calculate days taken for videos to trend
* Compare views and engagement patterns over time
* Build an interactive dashboard for visualization

---

## 🛠 Tools & Technologies Used

* Python (Pandas, Matplotlib, Seaborn)
* NLTK (VADER Sentiment Analysis)
* SQL (SQLite via SQLAlchemy)
* Microsoft Power BI
* Google Colab

---

## 📂 Dataset Used

* USvideos.csv (YouTube Trending Dataset – US Region)

Dataset includes:

* video_id
* title
* category_id
* views
* likes
* dislikes
* comment_count
* trending_date
* publish_time
* tags

---

## ⚙ Steps Performed

### 1️⃣ Data Cleaning

* Removed duplicates
* Handled missing values
* Converted date columns to datetime format
* Fixed timezone mismatch
* Standardized column formats

### 2️⃣ Feature Engineering

* Created `days_to_trend` feature
* Calculated `engagement_rate`
* Added country column

### 3️⃣ Sentiment Analysis

* Applied VADER sentiment analyzer on video titles
* Classified titles as:

  * Positive
  * Negative
  * Neutral

### 4️⃣ SQL Analysis

* Ranked categories by average views
* Counted total videos per category
* Aggregated data for insights

### 5️⃣ Visualization (Power BI Dashboard)

Dashboard includes:

* KPI Cards (Total Videos, Average Views, Avg Engagement)
* Bar Chart (Category vs Avg Views)
* Column Chart (Sentiment Distribution)
* Line Chart (Views Over Time)
* Scatter Plot (Engagement vs Views)
* Interactive Filters (Sentiment, Category, Date)

---

## 📈 Key Insights

* Certain categories dominate trending charts.
* Positive titles show slightly better engagement.
* Most videos trend within a short period after publishing.
* High views do not always guarantee high engagement.
* Engagement rate is a better indicator of audience interaction.

---

## 📦 Project Deliverables

* Python Notebook (.ipynb)
* Power BI Dashboard (PDF)
* SQL Queries File (.sql)
* Project Report (PDF)
* README File

---

## 🚀 How to Run the Project

1. Open Google Colab
2. Upload USvideos.csv
3. Run the Python notebook for:

   * Data cleaning
   * Sentiment analysis
   * Feature creation
4. Export cleaned dataset
5. Import dataset into Power BI
6. Create dashboard visuals
7. Export dashboard as PDF

---

## 📌 Conclusion

This project demonstrates how data analytics techniques can be used to understand digital content performance. By combining sentiment analysis, engagement metrics, and category-based ranking, the project provides insights that can help content creators and marketers optimize video strategies.



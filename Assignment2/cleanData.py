import pandas as pd

raw = pd.read_csv("kindle_reviews.csv", na_filter=False)
clean = raw.drop(columns=["helpful", "reviewTime", "reviewerID", "reviewerName", "unixReviewTime"])

clean.to_csv("clean_kindle_reviews.csv", index=False)
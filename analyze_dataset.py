import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('/home/ubuntu/RMP_sample_data.csv')

print("Dataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nUnique values in key columns:")
print("Unique professors:", df['professor_name'].nunique())
print("Unique schools:", df['school_name'].nunique())
print("Unique departments:", df['department_name'].nunique())

print("\nSample comments:")
for i, comment in enumerate(df['comments'].head(3)):
    print(f"Comment {i+1}: {comment[:200]}...")

# Save basic statistics
df.describe().to_csv('/home/ubuntu/dataset_statistics.csv')
print("\nBasic statistics saved to dataset_statistics.csv")


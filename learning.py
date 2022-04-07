
import pandas
from scipy.stats import pearsonr
from typing import Dict, Tuple

if __name__ == "__main__":

    data = pandas.read_csv("output_2022_04_07_14_41_08_016012_1370.csv")

    features = data.columns.values.tolist()[:-14]
    metrics = data.columns.values.tolist()[-14:]

    for metric in metrics:
        print(metric)

    data_features = data[features]

    correlation_pairs : Dict[Tuple, Tuple] = {}
    
    for feature in features:
        for metric in metrics:
            correlation_pairs[(feature, metric)] = pearsonr(data[feature], data[metric])
        
    for entry in correlation_pairs.items():
        if abs(entry[1][0]) > 0.9:
            print(f"{entry[1][0]} + {entry[1][1]} : {entry[0][0]} => {entry[0][1]}")
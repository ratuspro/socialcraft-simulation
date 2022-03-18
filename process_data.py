import pandas

if __name__ == "__main__":

    data = pandas.read_csv("data.csv")

    training_data = data.values[:, :-3]
    training_values = data.values[:, -1:]

    print(training_values)
    print(training_values)

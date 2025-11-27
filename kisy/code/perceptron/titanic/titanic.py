
import csv
import random
import matplotlib.pyplot as plt

FILENAME = "titanic.csv"

def load_titanic(filename):
    rows = []
    with open(filename, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def build_dataset(rows):
    ages, fares = [], []
    for r in rows:
        age_str = r["Age"].strip()
        if age_str:
            ages.append(float(age_str))
        fare_str = r["Fare"].strip()
        if fare_str:
            fares.append(float(fare_str))
    mean_age = sum(ages)/len(ages) if ages else 30.0
    mean_fare = sum(fares)/len(fares) if fares else 32.0

    X, y = [], []
    for r in rows:
        survived = int(r["Survived"])
        pclass = int(r["Pclass"])
        sex = 1 if r["Sex"].strip() == "female" else 0

        age_str = r["Age"].strip()
        age = float(age_str) if age_str else mean_age
        fare_str = r["Fare"].strip()
        fare = float(fare_str) if fare_str else mean_fare

        sibsp = int(r["SibSp"])
        parch = int(r["Parch"])
        family_size = sibsp + parch + 1

        # extra engineered features
        child = 1 if age < 16 else 0
        is_alone = 1 if family_size == 1 else 0

        # scaling
        pclass_feat = (3 - pclass) / 2.0      # 1->1, 2->0.5, 3->0
        age_feat = age / 80.0
        fare_feat = fare / 100.0
        family_feat = min(family_size, 8) / 8.0

        X.append([pclass_feat, sex, age_feat, fare_feat, family_feat, child, is_alone])
        y.append(survived)
    return X, y

def train_test_split(X, y, test_ratio=0.2):
    indices = list(range(len(X)))
    random.shuffle(indices)
    split = int(len(X)*(1-test_ratio))
    train_idx = indices[:split]
    test_idx = indices[split:]
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    return X_train, X_test, y_train, y_test

def perceptron_train(X_train, y_train, X_test, y_test, epochs=200, alpha=0.01):
    n_features = len(X_train[0])
    w = [0.0]*(n_features+1)
    train_accs, test_accs = [], []

    for epoch in range(epochs):
        # shuffle each epoch (stochastic-like)
        combined = list(zip(X_train, y_train))
        random.shuffle(combined)
        X_train, y_train = zip(*combined)
        X_train, y_train = list(X_train), list(y_train)

        for x, label in zip(X_train, y_train):
            x_vec = [1.0] + x
            y_val = sum(wi*xi for wi, xi in zip(w, x_vec))
            pred = 1 if y_val > 0 else 0
            error = label - pred
            if error != 0:
                for i in range(len(w)):
                    w[i] += alpha*error*x_vec[i]

        train_accs.append(accuracy(X_train, y_train, w))
        test_accs.append(accuracy(X_test, y_test, w))
    return w, train_accs, test_accs

def perceptron_predict_one(x, w):
    x_vec = [1.0] + x
    y_val = sum(wi*xi for wi, xi in zip(w, x_vec))
    return 1 if y_val > 0 else 0

def accuracy(X, y, w):
    correct = 0
    for xi, yi in zip(X, y):
        if perceptron_predict_one(xi, w) == yi:
            correct += 1
    return correct/len(y)

if __name__ == "__main__":
    rows = load_titanic(FILENAME)
    X, y = build_dataset(rows)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_ratio=0.2)

    weights, train_accs, test_accs = perceptron_train(
        X_train, y_train, X_test, y_test, epochs=200, alpha=0.01
    )

    print("Final weights:", weights)
    print("Train accuracy:", train_accs[-1])
    print("Test accuracy:", test_accs[-1])

    plt.plot(range(1, len(train_accs)+1), train_accs, label="Train")
    plt.plot(range(1, len(test_accs)+1), test_accs, label="Test")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


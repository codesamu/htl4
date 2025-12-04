
import csv

FILENAME = "titanic.csv"
OUTPUT_FILE = "titanic_numeric.txt"

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

    with open(OUTPUT_FILE, "w") as f:
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

            child = 1 if age < 16 else 0
            is_alone = 1 if family_size == 1 else 0

            pclass_feat = (3 - pclass) / 2.0
            age_feat = age / 80.0
            fare_feat = fare / 100.0
            family_feat = min(family_size, 8) / 8.0

            # Write: 7 features + label (space separated)
            features = [pclass_feat, sex, age_feat, fare_feat, family_feat, child, is_alone]
            line = " ".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in features) + f" {survived}"
            f.write(line + "\n")

if __name__ == "__main__":
    print("Loading titanic.csv...")
    rows = load_titanic(FILENAME)
    print(f"Loaded {len(rows)} rows")
    
    build_dataset(rows)
    print(f"Created {OUTPUT_FILE}")
    print("Now run the C program: gcc -O3 -o perceptron_titanic perceptron_titanic.c && ./perceptron_titanic")

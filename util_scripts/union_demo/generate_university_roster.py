import faker
import pandas as pd

fake = faker.Faker()

data = {
    "name": [fake.name() for _ in range(100)],
    "email": [fake.email() for _ in range(100)],
    "major": [fake.bs() for _ in range(100)],
    "grad_year": [fake.random_int(min=2025, max=2031) for _ in range(100)],
    "degree_type": [fake.random_element(elements=("BS", "BA", "MS", "PhD")) for _ in range(100)],
}

df = pd.DataFrame(data)

df.to_csv("university_roster.csv", index=False)

# Generate a new DataFrame with 80 rows using faker
new_data = {
    "name": [fake.first_name() for _ in range(80)],
    "email": [fake.email() for _ in range(80)],
    "grad_year": [fake.random_int(min=2025, max=2031) for _ in range(80)],
}
new_df_faker = pd.DataFrame(new_data)

# Select 20 rows from the existing DataFrame
df["first_name"] = df["name"].apply(lambda x: x.split()[0])
existing_data = df[["first_name", "email", "grad_year"]].sample(n=20)
existing_data = existing_data.rename(columns={"first_name": "name"})

# Combine the two DataFrames
final_df = pd.concat([new_df_faker, existing_data], ignore_index=True)

final_df.to_csv("union_roster.csv", index=False)

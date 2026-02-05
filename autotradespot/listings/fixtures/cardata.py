import json

import pandas as pd

df = pd.read_csv(r"CarData.csv", sep=";", index_col="Make")
gr = df.groupby("Make")
df2 = gr.apply(lambda x: x["Model"].unique())

Make_list = []
Model_list = []

index_make = 0
index_model = 0
for Make, Models in df2.items():
    if Models.size < 1:
        continue

    index_make += 1
    data_make = {"model": "listings.CarMake", "fields": {"name": Make, "makeId": index_make}}
    Make_list.append(data_make)
    for model in Models:
        index_model += 1
        data_model = {
            "model": "listings.CarModel",
            "fields": {"name": model, "modelId": index_model, "make": index_make},
        }
        Model_list.append(data_model)

with open("car_make_data.json", "w") as file:
    json.dump(Make_list, file)

with open("car_model_data.json", "w") as file:
    json.dump(Model_list, file)

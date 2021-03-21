import os
import requests
from src.dataCollector import DataCollector


root_dir = f"{os.path.dirname(os.path.realpath(__file__))}/media"
collector = DataCollector()

def create_dir(dir_loc):
    if not os.path.exists(dir_loc):
        os.mkdir(dir_loc)

def download_all(data):
    for d in data:
        for media in d["media"]:
            dir_loc = f'{root_dir}/{media["type"]}'
            create_dir(dir_loc)
            with open(f'{dir_loc}/{media["link"].split("/")[-1]}', "xb") as f:
                f.write(requests.get(media["link"]).content)


if __name__ == "__main__":
    create_dir(root_dir)
    download_all(collector.get_all())
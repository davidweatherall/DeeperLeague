
import os
import json

if __name__ == "__main__":
    champs_in_dir = os.listdir("champions")
    champMap = {}
    for i in range(len(champs_in_dir)):
        number_of_champ_images = len(os.listdir("champions/{0}".format(champs_in_dir[i])))
        champMap[i] = {
            'champ_name': champs_in_dir[i],
            'champ_images': number_of_champ_images
        }

    print([champ for champ in champs_in_dir])

    with open("champMap.json", "w") as f:
        f.write(json.dumps(champMap))
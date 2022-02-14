import yaml, json
import os, shutil


def update_front_end():
    print("Updating front end...")

    # send the build folder
    copy_folders_from_src_to_dst("./build", "./front_end/src/chain-info")

    # send our brownie-config.yaml to the front end, in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)

        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)

    print("... Done! Front end updated.\n")


def copy_folders_from_src_to_dst(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)


def main():
    update_front_end()

import os
import yaml
from dataclasses import dataclass
import clipboard as cb
from rapidfuzz import process

CONFIG_PATH = "config.yaml"
M_WORD = "word"
M_CHAR = "char"

@dataclass
class ConfigFile():
    character_set_directory: str
    current_selection: str
    mode: str
    auto_set_mode: bool


    def update_config(self) -> None:
        out = self.__dict__
        write_file(CONFIG_PATH, out)


    def get_character_sets(self) -> None:
        if self.character_set_directory == None:
            print("Error: character_set_directory not set")
            return

        files = os.listdir(self.character_set_directory)
        counter = 1

        for name in files:
            temp_name = None
            
            if "." in name:
                temp_name = name.split(".")[0]

            if temp_name != None:
                print(f"[{counter}] {temp_name}")

            counter += 1

    
    def select_character_set(self) -> bool:
        index = input("Please select a character set> ")
        
        try:
            index = int(index) - 1
        except Exception as e:
            print(f"Error: unable to convert {index} to int - {e}")
            return False
        
        files = os.listdir(self.character_set_directory)

        if index < 0:
            index = 0
        elif index >= len(files):
            index = len(files)-1

        if files[index] != None:
            self.current_selection = f"{self.character_set_directory}/{files[index]}"

            if self.auto_set_mode:

                if files[index].startswith("ch_"):
                    self.mode = "char"
                    print(f"Info: {self.mode} set selected - auto set mode to {self.mode}")
                elif files[index].startswith("wd_"):
                    self.mode = "word"
                    print(f"Info: {self.mode} set selected - auto set mode to {self.mode}")

            return True
        else:
            return False
        

    def output_string(self, input_string: str) -> str:
        output = ""
        w_output = []
        
        if self.current_selection == None:
            status = self.select_character_set()

            if status == True:
                self.update_config()
            else:
                print("Error: failed to select character set")
                return None
            
        
        input_data = input_string
        character_buf = read_file(self.current_selection)
        character_set = parse_yaml(character_buf)

        if self.mode == "char":
            input_data = input_data.upper()

            for i in input_data:
                temp_data = catch_key_exception(character_set, i)

                if temp_data != None:
                    output += f"{temp_data} "

            return output


        elif self.mode == "word":
            split_input = input_data.lower().split(" ")
            output = input_data

            for key in split_input:
                value = catch_key_exception(character_set, key)

                if value:
                    w_output += [value]
                    w_output += [" "]
                else:
                    pair = process.extractOne(key, character_set, score_cutoff=80)

                    if pair:
                        w_output += [pair[0]]
                        w_output += [" "]

            return "".join(w_output)


def load_config() -> ConfigFile:
    buffer = read_file(CONFIG_PATH)
    config_data = parse_yaml(buffer)

    return ConfigFile(
        character_set_directory = catch_key_exception(config_data, "character_set_directory"),
        current_selection = catch_key_exception(config_data, "current_selection"),
        mode = catch_key_exception(config_data, "mode"),
        auto_set_mode = catch_key_exception(config_data, "auto_set_mode")
    )


def read_file(file_name: str) -> str:
    buffer = ""

    with open(file_name, "r") as f:
        buffer = f.read()

    return buffer


def parse_yaml(data: str) -> dict[str]:
    output = None

    try:
        output = yaml.safe_load(data)
        return output
    except Exception as e:
        print(f"Error: unable to parse yaml to python diconary - {e}")
        return None


def write_file(file_name: str, contents: ConfigFile) -> bool:
    data = yaml.dump(contents)

    with open(CONFIG_PATH, "w") as f:
        bytes_write = f.write(data)

        if bytes_write > 0:
            print(f"Successfully wrote {bytes_write} bytes to {file_name}")
            return True
        else:
            print(f"Failed to write to file {file_name}")
            return False


def catch_key_exception(data: dict, key: str) -> str:
    output = None

    try:
        output = data[key]
        return output
    except KeyError as e:
        print(f"Unable to find key {key} in dictonary - {e}")
        return None
    

def shell(config: ConfigFile) -> None:
    if config.current_selection == None:
        config.get_character_sets()
        config.select_character_set()
        config.update_config()
    
    user_input = ""
    output = ""
    print("Entering shell...\n")

    while user_input != "exit":
        user_input = input("> ")

        if user_input == "":
            continue

        elif user_input == "config":
            print("Did you mean the following?")
            print("config set - sets the character set")
            print("config mode - sets the mode [char or word]")
            continue

        elif user_input == "config set":
            config.get_character_sets()
            status = config.select_character_set()

            if status == True:
                config.update_config()
            else:
                print("Error: failed to update config file")

            continue

        elif user_input == "config mode":
            print("word - replaces whole words\nchar - replaces individual characters")
            user_input = input("Please select a mode> ")

            if user_input.lower() == "word":
                config.mode = "word"
            elif user_input.lower() == "char":
                config.mode = "char"
            else:
                print("Error: invalid mode")

            config.update_config()
            continue
        
        output = config.output_string(user_input)
        cb.copy(output)
        print(output)

    print("Exiting...\n")
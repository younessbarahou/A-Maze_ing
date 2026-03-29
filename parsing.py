from pydantic import BaseModel, Field, model_validator
from typing import Optional


class Config(BaseModel):
    Width: int = Field(ge=2)
    Height: int = Field(ge=2)
    Entry: tuple[int, int]
    Exit: tuple[int, int]
    Output_file: str
    Perfect: bool
    Seed: Optional[int] = None

    @model_validator(mode='after')
    def validator(self) -> "Config":
        if self.Entry[0] == self.Exit[0] and self.Exit[1] == self.Entry[1]:
            raise ValueError("Entry should be different from Exit !")
        return self


def entry_exit_validator(entry: str, exit: str) -> dict | None:
    entry_check: list = entry.split(',')
    if len(entry_check) != 2:
        raise ValueError("Entry coordinates are not valid x,y!")
    try:
        entry_check[0] = int(entry_check[0])
        entry_check[1] = int(entry_check[1])
    except ValueError:
        raise ValueError("Entry coordinates should be valid integers!")
    exit_check = exit.split(',')
    if len(exit_check) != 2:
        raise ValueError("Exit coordinates are not valid x,y!")
    try:
        exit_check[0] = int(exit_check[0])
        exit_check[1] = int(exit_check[1])
    except ValueError:
        raise ValueError("Exit coordinates should be valid integers!")
    entry_check: tuple = tuple(entry_check)
    exit_check: tuple = tuple(exit_check)
    return {'entry': entry_check,
            'exit': exit_check}


def perfect_validator(perfect: str) -> bool | None:
    if perfect == "True":
        return True
    elif perfect == "False":
        return False
    else:
        raise ValueError("Perfect parameter should be True/False!")


def comments_remover(lines: list) -> list:
    return [line for line in lines if line[0] != '#']


def parser(config_file: str) -> Config | None:
    """ basic parameters that should be in a config file """
    mandatory_keys = {
        "WIDTH": False,
        "HEIGHT": False,
        "ENTRY": False,
        "EXIT": False,
        "OUTPUT_FILE": False,
        "PERFECT": False
    }
    optional_keys = {
        "SEED": False
    }
    """ open and read config file """
    with open(config_file, 'r') as file:
        lines: list = file.readlines()
        lines = comments_remover(lines)
        if len(lines) == 0:
            raise ValueError("Config file is empty !")
        lines: list = list(map(lambda x: x.split("="), lines))
        """ check for x=y pattern validation"""
        for line in lines:
            if len(line) != 2 or line[0] == "" or line[1] == "":
                raise ValueError(f"Invalid parameter '{line[0].strip()}'")
            line[0] = line[0].strip()
            line[1] = line[1].strip()
        """ check mandatory parameters """
        lines_dict: dict = {line[0]: line[1] for line in lines}
        for key in lines_dict:
            if key in mandatory_keys:
                mandatory_keys[key] = True
            elif key in optional_keys:
                optional_keys[key] = True
            else:
                raise ValueError(f"{key} is not a valid parameter!")
        missing_keys: list = [
            k for k in mandatory_keys if mandatory_keys[k] is False]
        if len(missing_keys) > 0:
            raise ValueError(
                f"Parameters are missing: {','.join(missing_keys)}")
        """ check parameter's values manual for entry and exit """
        """ other parameters are checked automatic using pydantic"""
        entry_exit = entry_exit_validator(
            lines_dict['ENTRY'], lines_dict['EXIT'])
        perfect = perfect_validator(lines_dict['PERFECT'])
        """ setting the data product"""
        final_validation: Config = Config(
            Width=lines_dict['WIDTH'],
            Height=lines_dict['HEIGHT'],
            Entry=entry_exit['entry'],
            Exit=entry_exit['exit'],
            Output_file=lines_dict['OUTPUT_FILE'],
            Perfect=perfect,
            Seed=lines_dict['SEED'] if optional_keys['SEED'] else None)
        return final_validation

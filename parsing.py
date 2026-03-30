from pydantic import BaseModel, Field, model_validator
from typing import Optional, Tuple, List, Dict


class Config(BaseModel):
    """ holds the valid parameters from config file """
    Width: int = Field(ge=2)
    Height: int = Field(ge=2)
    Entry: Tuple[int, int]
    Exit: Tuple[int, int]
    Output_file: str
    Perfect: bool
    SEED: Optional[int] = None

    @model_validator(mode='after')
    def validator(self) -> "Config":
        """ setting an additional validation """
        if self.Entry[0] == self.Exit[0] and self.Exit[1] == self.Entry[1]:
            raise ValueError("Entry should be different from Exit !")
        return self


def entry_exit_validator(entry: str, exit: str) -> Dict[str, tuple[int, int]]:
    """ validates both entry and exit parameters """
    entry_check: List[str] = entry.split(',')
    exit_check: List[str] = exit.split(',')
    entry_to_int: Tuple[int, int] = (-1, -1)
    exit_to_int: Tuple[int, int] = (-1, -1)
    if len(entry_check) != 2:
        raise ValueError("Entry coordinates are not valid x,y!")
    try:
        entry_to_int = (int(entry_check[0]), int(entry_check[1]))
    except ValueError:
        raise ValueError("Entry coordinates should be valid integers!")
    if len(exit_check) != 2:
        raise ValueError("Exit coordinates are not valid x,y!")
    try:
        exit_to_int = (int(exit_check[0]), int(exit_check[1]))
    except ValueError:
        raise ValueError("Exit coordinates should be valid integers!")
    return {'entry': entry_to_int,
            'exit': exit_to_int}


def perfect_validator(perfect: str) -> bool:
    """ validate the perfect parameter """
    if perfect == "True":
        return True
    elif perfect == "False":
        return False
    else:
        raise ValueError("Perfect parameter should be True/False!")


def comments_remover(lines: List[str]) -> List[str]:
    """ discards the comments """
    return [line for line in lines if line[0] != '#']


def parser(config_file: str) -> Config:
    """ parses and validate the parameters in the config file """
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
    try:
        with open(config_file, 'r') as file:
            lines: List[str] = file.readlines()
            lines_no_cmt: List[str] = comments_remover(lines)
            if len(lines_no_cmt) == 0:
                raise ValueError("Config file is empty !")
            splitted_lines: List[List[str]] = list(
                map(lambda x: x.split("=", 1), lines_no_cmt)
            )
            for line in splitted_lines:
                if len(line) != 2 or line[0] == "" or line[1] == "":
                    raise ValueError(f"Invalid parameter '{line[0].strip()}'")
                line[0] = line[0].strip()
                line[1] = line[1].strip()
            lines_dict: Dict[str, str] = {
                line[0]: line[1] for line in splitted_lines}
            for key in lines_dict:
                if key in mandatory_keys:
                    mandatory_keys[key] = True
                elif key in optional_keys:
                    optional_keys[key] = True
                else:
                    raise ValueError(f"{key} is not a valid parameter!")
            missing_keys: List[str] = [
                k for k in mandatory_keys if mandatory_keys[k] is False]
            if len(missing_keys) > 0:
                raise ValueError(
                    f"Parameters are missing: {','.join(missing_keys)}")
            entry_exit: Dict[str, tuple[int, int]] = entry_exit_validator(
                lines_dict['ENTRY'], lines_dict['EXIT'])
            perfect: bool = perfect_validator(lines_dict['PERFECT'])
            try:
                width_int: int = int(lines_dict['WIDTH'])
            except ValueError:
                raise ValueError("Width should be a valid integer!")
            try:
                height_int: int = int(lines_dict['HEIGHT'])
            except ValueError:
                raise ValueError("Height should be a valid integer!")
            if 'SEED' in lines_dict:
                try:
                    seed_result: int | None = int(lines_dict['SEED'])
                except ValueError:
                    raise ValueError("Seed should be a valid integer!")
            final_validation: Config = Config(
                Width=width_int,
                Height=height_int,
                Entry=entry_exit['entry'],
                Exit=entry_exit['exit'],
                Output_file=lines_dict['OUTPUT_FILE'],
                Perfect=perfect,
                SEED=seed_result if 'SEED' in lines_dict else None)
            return final_validation
    except FileNotFoundError:
        raise FileNotFoundError("Config file is missing !")
    except PermissionError:
        raise PermissionError("Can not read config file (permission error)")

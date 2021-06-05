from typing import List, Iterable
from fuzzywuzzy import fuzz
import tlsh


def get_hash(string: str) -> str:
    hash_ = tlsh.hash(string.encode("utf-8"))
    return hash_ if hash_ != "TNULL" else f"N{string}"


def parse_file_name(file_name: str) -> List[str]:
    temp = file_name.rsplit(",", 1)

    if len(temp) == 1:
        temp.insert(0, "")

    return temp


def compare_hashes(hash1: str, hash2: str) -> bool:
    if hash1[0] != hash2[0]:
        return False

    if hash1[0] == "T":
        diff = tlsh.diff(hash1, hash2)

        return diff < 100  # TODO - find good values here
    else:
        ratio = fuzz.ratio(hash1, hash2)
        return ratio > 70  # TODO - find good ratio here

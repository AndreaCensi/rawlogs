from comptests import comptests_for_all
from rawlogs import get_conftools_rawlogs

__all__ = [
    'for_all_rawlogs',
]


for_all_rawlogs = comptests_for_all(get_conftools_rawlogs())

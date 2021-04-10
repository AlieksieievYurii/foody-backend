from enum import Enum
from typing import List


class UserType(Enum):
    client: str = 'client'
    executor: str = 'executor'
    administrator: str = 'administrator'

    @classmethod
    def values(cls) -> List[str]:
        return [v.value for v in cls]

if __name__ == '__main__':
    print()
from enum import Enum


class Status(Enum):

    @classmethod
    def filtered_list(cls, *excludes):
        return [status.value for status in list(cls) if status not in excludes]

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

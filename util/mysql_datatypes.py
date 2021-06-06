# Some datatypes to be used internally

class DataType:
    def __init__(self, not_null=False):
        self.not_null = not_null


class VarChar(DataType):
    def __init__(self, num_chars: int, not_null=False):
        super().__init__(not_null)
        self.num_chars = num_chars

    def __str__(self):
        return f"VARCHAR({self.num_chars}) {'NOT NULL' if self.not_null else ''}"


class Date(DataType):
    def __str__(self):
        return f"DATE {'NOT NULL' if self.not_null else ''}"


class DateTime(DataType):
    def __str__(self):
        return f"DATETIME {'NOT NULL' if self.not_null else ''}"


class Bool(DataType):
    def __init__(self, val, not_null=False):
        super().__init__(not_null)
        self.val = val

    def __str__(self):
        return "BOOL" if self.val is None else "TRUE" if self.val else "FALSE"

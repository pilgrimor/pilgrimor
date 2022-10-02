import re
from pydantic import BaseModel


class BaseTable(type):
    """Base class for table declaration."""

    def __new__(cls, clsname, bases, attrs):
        """
        Creates new
        """
        table_name = "_".join(
            [
                name.lower() for name
                in re.findall("[a-zA-Z][^A-Z]*", clsname)
            ]
        )
        attrs["table_name"] = table_name

        return super().__new__(cls, clsname, bases, attrs)

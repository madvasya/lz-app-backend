from typing import TypeAlias, Annotated
from pydantic import StringConstraints

PasswordStr: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=8, max_length=30)
]
UserNameStr: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=4, max_length=30)
]
NameStr: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=30)
]
FullNameStr: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=30)
]
DescriptionStr: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=100)
]

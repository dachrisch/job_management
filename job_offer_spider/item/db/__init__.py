from dataclasses import dataclass
from typing import Protocol, ClassVar, Dict, Any, runtime_checkable


@dataclass
class HasUrl:
    url: str

@runtime_checkable
@dataclass
class IsDataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[Dict[str, Any]]

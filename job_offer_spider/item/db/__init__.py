from dataclasses import dataclass, InitVar
from typing import Protocol, ClassVar, Dict, Any, runtime_checkable

from montydb.types.objectid import ObjectId


@dataclass
class HasUrl:
    url: str = None


@dataclass
class HasId:
    _id: InitVar[ObjectId | None] = None

    def __post_init__(self, _id: ObjectId | None):
        self.id = _id


@runtime_checkable
@dataclass
class IsDataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[Dict[str, Any]]

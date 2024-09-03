from dataclasses import dataclass, field
from typing import Protocol, ClassVar, Dict, Any, runtime_checkable, Optional

from dataclasses_json import dataclass_json, config
from montydb.types.objectid import ObjectId


@dataclass_json
@dataclass
class HasUrl:
    url: str = field()

    def __post_init__(self):
        if not self.url:
            raise ValueError(f'No value for url: {self}')


@dataclass_json
@dataclass
class HasId:
    id: Optional[ObjectId] = field(default=None, metadata=config(field_name='_id', exclude=lambda x: True))


@runtime_checkable
@dataclass
class IsDataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[Dict[str, Any]]

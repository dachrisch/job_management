from unittest import TestCase

from pydantic.v1 import Field
from pydantic.v1 import BaseModel


class Address(BaseModel):
    street: str=None


class User(BaseModel):
    name: str=None
    address: Address=Field(default_factory=lambda : Address())


class PydanticFieldTest(TestCase):

    def test_field_attributes(self):
        self.assertEqual(User(), User())

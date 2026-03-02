"""Tests for BaseModel to_dict() and __repr__() methods."""

import unittest
from pajgps_api.models.base import BaseModel


class TestBaseModel(unittest.TestCase):
    """Tests for BaseModel helper methods."""

    def test_to_dict_returns_instance_attributes(self):
        """to_dict() should return all attributes set on the model."""
        model = BaseModel(foo="bar", baz=42)
        result = model.to_dict()
        self.assertEqual(result, {"foo": "bar", "baz": 42})

    def test_to_dict_empty_model(self):
        """to_dict() on a model with no attributes should return an empty dict."""
        model = BaseModel()
        self.assertEqual(model.to_dict(), {})

    def test_repr_includes_class_name_and_attributes(self):
        """__repr__() should include the class name and dict of attributes."""
        model = BaseModel(x=1, y=2)
        representation = repr(model)
        self.assertIn("BaseModel", representation)
        self.assertIn("x", representation)
        self.assertIn("y", representation)

    def test_repr_format(self):
        """__repr__() should follow the expected <ClassName({...})> format."""
        model = BaseModel(name="test")
        self.assertTrue(repr(model).startswith("<BaseModel("))
        self.assertTrue(repr(model).endswith(")>"))


if __name__ == "__main__":
    unittest.main()

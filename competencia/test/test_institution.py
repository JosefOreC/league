"""
Tests unitarios para Institution (domain/entities/institution.py)
"""
import unittest
from ..domain.entities.institution import Institution
from ..domain.value_objects.enums.institution_category import InstitutionCategory


class TestInstitution(unittest.TestCase):

    def test_create_institution_ok(self):
        inst = Institution(
            id=1,
            name="Universidad Test",
            category=InstitutionCategory.SECONDARY,
            city="Ciudad Test",
            code="UNI-001"
        )
        self.assertEqual(inst.id, 1)
        self.assertEqual(inst.name, "Universidad Test")
        self.assertEqual(inst.category, InstitutionCategory.SECONDARY)
        self.assertEqual(inst.city, "Ciudad Test")
        self.assertEqual(inst.code, "UNI-001")

    def test_set_id_ok(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        inst.id = 2
        self.assertEqual(inst.id, 2)

    def test_set_id_invalid_raises(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        with self.assertRaises(ValueError):
            inst.id = None
        with self.assertRaises(ValueError):
            inst.id = "invalid"

    def test_set_name_ok(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        inst.name = "Nuevo Nombre"
        self.assertEqual(inst.name, "Nuevo Nombre")

    def test_set_name_invalid_raises(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        with self.assertRaises(ValueError):
            inst.name = ""
        with self.assertRaises(ValueError):
            inst.name = None

    def test_set_category_ok(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        inst.category = InstitutionCategory.MIXED
        self.assertEqual(inst.category, InstitutionCategory.MIXED)

    def test_set_category_invalid_raises(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        with self.assertRaises(ValueError):
            inst.category = "invalid_category"

    def test_set_city_ok(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        inst.city = "Nueva Ciudad"
        self.assertEqual(inst.city, "Nueva Ciudad")

    def test_set_city_invalid_raises(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        with self.assertRaises(ValueError):
            inst.city = ""

    def test_set_code_ok(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        inst.code = "N-002"
        self.assertEqual(inst.code, "N-002")

    def test_set_code_invalid_raises(self):
        inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C-1")
        with self.assertRaises(ValueError):
            inst.code = ""

if __name__ == "__main__":
    unittest.main()

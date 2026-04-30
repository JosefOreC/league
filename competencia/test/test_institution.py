"""
Tests unitarios para Institution (domain/entities/institution.py)
"""
import unittest
from competencia.domain.entities.institution import Institution


class TestInstitution(unittest.TestCase):

    def test_create_institution_ok(self):
        inst = Institution(
            id="1",
            name="Universidad Test",
            type="SECONDARY",
            city="Ciudad Test",
            country="Peru"
        )
        self.assertEqual(inst.id, "1")
        self.assertEqual(inst.name, "Universidad Test")
        self.assertEqual(inst.type, "SECONDARY")
        self.assertEqual(inst.city, "Ciudad Test")
        self.assertEqual(inst.country, "Peru")

    def test_to_dict(self):
        inst = Institution(id="1", name="Inst", type="PRIMARY", city="C", country="Peru")
        d = inst.to_dict()
        self.assertEqual(d["id"], "1")
        self.assertEqual(d["name"], "Inst")
        self.assertEqual(d["type"], "PRIMARY")

if __name__ == "__main__":
    unittest.main()

import unittest

from app import resolve_driver_form_context


class DriverContextTests(unittest.TestCase):
    def test_prefers_master_data_when_driver_exists(self):
        driver_data = {
            'nopol': 'B1234XYZ',
            'vehicle_type': 'INNOVA',
            'bbm_type': 'PERTAMAX',
        }

        result = resolve_driver_form_context(
            driver_data,
            driver_name='ALICE',
            nopol='A1111AA',
            vehicle_type='AVANZA',
            bbm_type='PERTALITE',
        )

        self.assertEqual(result['nopol'], 'B1234XYZ')
        self.assertEqual(result['vehicle_type'], 'INNOVA')
        self.assertEqual(result['bbm_type'], 'PERTAMAX')

    def test_keeps_form_values_when_driver_is_missing(self):
        result = resolve_driver_form_context(
            None,
            driver_name='BOB',
            nopol='A2222BB',
            vehicle_type='AVANZA',
            bbm_type='PERTALITE',
        )

        self.assertEqual(result['nopol'], 'A2222BB')
        self.assertEqual(result['vehicle_type'], 'AVANZA')
        self.assertEqual(result['bbm_type'], 'PERTALITE')


if __name__ == '__main__':
    unittest.main()

"""
backend/integrations/hospital_data.py - Manager de datos de hospitales
Maneja la información de hospitales, especialidades y costos
"""

from typing import List, Dict

class HospitalDataManager:
    """Gestor de datos de hospitales y especialidades"""
    
    def __init__(self):
        """Inicializar manager con datos de ejemplo"""
        self.hospitals = self._load_sample_hospitals()
        self.specialties = self._load_sample_specialties()
    
    def get_hospitals(self) -> List[Dict]:
        """Obtener lista de hospitales disponibles"""
        return self.hospitals
    
    def get_specialties(self) -> List[Dict]:
        """Obtener lista de especialidades médicas"""
        return self.specialties
    
    def get_hospital_by_id(self, hospital_id: str) -> Dict:
        """Obtener hospital específico por ID"""
        for h in self.hospitals:
            if h.get('id') == hospital_id:
                return h
        return {}
    
    def _load_sample_hospitals(self) -> List[Dict]:
        """Cargar datos reales de hospitales en Ecuador (Quito)"""
        return [
            {
                "id": "hosp_001",
                "nombre": "Hospital Metropolitano",
                "red": "Red Premium",
                "copago_base": 25.0,
                "telefono": "+593 2 399-8000",
                "direccion": "Av. Mariana de Jesús y Nicolás Arteta S/N, Quito"
            },
            {
                "id": "hosp_002",
                "nombre": "Hospital Vozandes",
                "red": "Red Plus",
                "copago_base": 15.0,
                "telefono": "+593 2 400-7100",
                "direccion": "Calle Veracruz N37-102 y Av. América, Quito"
            },
            {
                "id": "hosp_003",
                "nombre": "Hospital de Clínicas Pichincha",
                "red": "Red Básica",
                "copago_base": 12.0,
                "telefono": "+593 2 299-8700",
                "direccion": "Gral. Ulpiano Páez N22-188 y Veintimilla, Quito"
            },
            {
                "id": "hosp_004",
                "nombre": "Hospital Pediátrico Baca Ortiz",
                "red": "Red Pública",
                "copago_base": 0.0,  # Gratuito por ley de la Red Pública Integral de Salud (MSP)
                "telefono": "+593 2 394-2800",
                "direccion": "Av. 6 de Diciembre S/N y Av. Cristóbal Colón, Quito"
            }
        ]
    
    def _load_sample_specialties(self) -> List[Dict]:
        """Cargar datos reales de especialidades y costos promedio del mercado privado ecuatoriano"""
        return [
            {
                "nombre": "Medicina General",
                "codigo": "MED_GEN",
                "costo_base": 40.0,
                "sintomas_clave": ["dolor", "fiebre", "malestar"]
            },
            {
                "nombre": "Cardiología",
                "codigo": "CARD",
                "costo_base": 75.0,
                "sintomas_clave": ["dolor de pecho", "arritmia", "presión alta"]
            },
            {
                "nombre": "Traumatología",
                "codigo": "TRAUMA",
                "costo_base": 65.0,
                "sintomas_clave": ["fractura", "esguince", "dolor articular"]
            },
            {
                "nombre": "Gastroenterología",
                "codigo": "GASTRO",
                "costo_base": 70.0,
                "sintomas_clave": ["dolor abdominal", "gastritis", "diarrea"]
            },
            {
                "nombre": "Oftalmología",
                "codigo": "OFTALMOLOGIA",
                "costo_base": 60.0,
                "sintomas_clave": ["visión borrosa", "dolor ocular", "conjuntivitis"]
            },
            {
                "nombre": "Dermatología",
                "codigo": "DERMA",
                "costo_base": 65.0,
                "sintomas_clave": ["erupción", "acné", "prurito"]
            }
        ]
    
    def suggest_specialty(self, symptom: str) -> Dict:
        """Sugerir especialidad basada en síntoma (lógica simple)"""
        symptom_lower = symptom.lower()
        
        for specialty in self.specialties:
            for key_symptom in specialty.get('sintomas_clave', []):
                if key_symptom in symptom_lower:
                    return specialty
        
        # Por defecto, medicina general
        return self.specialties[0]
    
    def get_cheapest_hospital(self) -> Dict:
        """Obtener hospital más económico"""
        return min(self.hospitals, key=lambda x: x.get('copago_base', 0))
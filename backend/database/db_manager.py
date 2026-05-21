"""
backend/database/db_manager.py - Manager de SQLite
Gestiona la base de datos local para planes de seguro, hospitales y especialidades
"""

import sqlite3
import os
from typing import List, Dict
from pathlib import Path

class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path: str = "data/viamatica.db"):
        """
        Inicializar conexión a base de datos
        
        Args:
            db_path: Ruta del archivo SQLite
        """
        self.db_path = db_path
        
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
    
    def _get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Retornar filas como diccionarios
        return conn
    
    def _init_database(self):
        """Crear tablas si no existen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de hospitales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitales (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                red TEXT NOT NULL,
                copago_base REAL NOT NULL,
                telefono TEXT,
                direccion TEXT,
                ciudad TEXT
            )
        """)
        
        # Tabla de especialidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS especialidades (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                codigo TEXT UNIQUE NOT NULL,
                costo_base REAL NOT NULL,
                sintomas_clave TEXT,
                descripcion TEXT
            )
        """)
        
        # Tabla de planes de seguro
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planes_seguro (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                compania TEXT NOT NULL,
                cobertura_porcentaje REAL NOT NULL,
                deducible REAL,
                copago_fijo REAL,
                descripcion TEXT
            )
        """)
        
        # Tabla de cobertura por especialidad y plan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cobertura_especialidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                especialidad_id TEXT NOT NULL,
                cubre_porcentaje REAL NOT NULL,
                copago_especialidad REAL,
                FOREIGN KEY (plan_id) REFERENCES planes_seguro(id),
                FOREIGN KEY (especialidad_id) REFERENCES especialidades(id),
                UNIQUE(plan_id, especialidad_id)
            )
        """)
        
        conn.commit()
        
        # Cargar datos de ejemplo automáticamente si está vacía
        cursor.execute("SELECT COUNT(*) FROM hospitales")
        if cursor.fetchone()[0] == 0:
            print("[INFO] Base de datos vacía. Cargando datos de ejemplo...")
            conn.close()
            self.load_sample_data()
        else:
            conn.close()
        print("[OK] Base de datos inicializada")
    
    # ========== HOSPITALES ==========
    def get_hospitales(self) -> List[Dict]:
        """Obtener todos los hospitales"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospitales")
        hospitales = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return hospitales
    
    def get_hospital_by_id(self, hospital_id: str) -> Dict:
        """Obtener hospital por ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospitales WHERE id = ?", (hospital_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def add_hospital(self, id: str, nombre: str, red: str, copago_base: float, 
                     telefono: str = None, direccion: str = None, ciudad: str = None):
        """Agregar nuevo hospital"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO hospitales 
            (id, nombre, red, copago_base, telefono, direccion, ciudad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id, nombre, red, copago_base, telefono, direccion, ciudad))
        conn.commit()
        conn.close()
    
    # ========== ESPECIALIDADES ==========
    def get_especialidades(self) -> List[Dict]:
        """Obtener todas las especialidades"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM especialidades")
        especialidades = []
        for row in cursor.fetchall():
            spec = dict(row)
            spec['sintomas_clave'] = spec['sintomas_clave'].split(',') if spec['sintomas_clave'] else []
            especialidades.append(spec)
        conn.close()
        return especialidades
    
    def add_especialidad(self, id: str, nombre: str, codigo: str, costo_base: float,
                         sintomas_clave: List[str] = None, descripcion: str = None):
        """Agregar nueva especialidad"""
        conn = self._get_connection()
        cursor = conn.cursor()
        sintomas_str = ','.join(sintomas_clave) if sintomas_clave else ""
        cursor.execute("""
            INSERT OR REPLACE INTO especialidades 
            (id, nombre, codigo, costo_base, sintomas_clave, descripcion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, nombre, codigo, costo_base, sintomas_str, descripcion))
        conn.commit()
        conn.close()
    
    # ========== PLANES DE SEGURO ==========
    def get_planes_seguro(self) -> List[Dict]:
        """Obtener todos los planes de seguro"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM planes_seguro")
        planes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return planes
    
    def get_plan_by_id(self, plan_id: str) -> Dict:
        """Obtener plan de seguro por ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM planes_seguro WHERE id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def add_plan_seguro(self, id: str, nombre: str, compania: str, cobertura_porcentaje: float,
                        deducible: float = None, copago_fijo: float = None, descripcion: str = None):
        """Agregar nuevo plan de seguro"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO planes_seguro 
            (id, nombre, compania, cobertura_porcentaje, deducible, copago_fijo, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id, nombre, compania, cobertura_porcentaje, deducible, copago_fijo, descripcion))
        conn.commit()
        conn.close()
    
    # ========== COBERTURA POR ESPECIALIDAD ==========
    def get_cobertura(self, plan_id: str, especialidad_id: str) -> Dict:
        """Obtener cobertura para un plan y especialidad específicos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cobertura_especialidad 
            WHERE plan_id = ? AND especialidad_id = ?
        """, (plan_id, especialidad_id))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def add_cobertura(self, plan_id: str, especialidad_id: str, cubre_porcentaje: float, 
                     copago_especialidad: float = None):
        """Agregar cobertura para plan y especialidad"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cobertura_especialidad 
            (id, plan_id, especialidad_id, cubre_porcentaje, copago_especialidad)
            VALUES (?, ?, ?, ?)
        """, (plan_id, especialidad_id, cubre_porcentaje, copago_especialidad))
        conn.commit()
        conn.close()
    
    # ========== UTILIDADES ==========
    def load_sample_data(self):
        """Cargar datos de ejemplo reales de Ecuador"""
        # Hospitales
        # Notas de corrección: 
        # - El Metropolitano y Vozandes usan PBX unificado moderno (02-399-8000 y 02-400-7100).
        # - Clínica Pichincha está en la calle Ulpiano Páez y Veintimilla.
        # - Baca Ortiz es público (MSP), copago base de consulta externa es $0 por ley de gratuidad.
        # - Copagos base privados configurados según los promedios de deducible por consulta de redes prepagadas.
        hospitales = [
            ("hosp_001", "Hospital Metropolitano", "Red Premium", 25.0, "+593 2 399-8000", "Av. Mariana de Jesús y Nicolás Arteta S/N", "Quito"),
            ("hosp_002", "Hospital Vozandes", "Red Plus", 15.0, "+593 2 400-7100", "Calle Veracruz N37-102 y Av. América", "Quito"),
            ("hosp_003", "Hospital de Clínicas Pichincha", "Red Básica", 12.0, "+593 2 299-8700", "Gral. Ulpiano Páez N22-188 y Veintimilla", "Quito"),
            ("hosp_004", "Hospital Pediátrico Baca Ortiz", "Red Pública", 0.0, "+593 2 394-2800", "Av. 6 de Diciembre S/N y Av. Cristóbal Colón", "Quito"),
        ]
        
        for hosp in hospitales:
            self.add_hospital(*hosp)
        
        # Especialidades
        # Costos ajustados al mercado ecuatoriano (Med. General $35-$45, Especialistas privados $60-$80)
        especialidades = [
            ("esp_001", "Medicina General", "MED_GEN", 40.0, ["dolor", "fiebre", "malestar"], "Consulta general"),
            ("esp_002", "Cardiología", "CARD", 75.0, ["pecho", "corazón", "presión"], "Especialista del corazón"),
            ("esp_003", "Dermatología", "DERM", 65.0, ["piel", "acné", "alergia"], "Especialista de la piel"),
            ("esp_004", "Ginecología", "GIN", 70.0, ["ginecología", "reproductivo"], "Especialista femenino"),
            ("esp_005", "Oftalmología", "OFT", 60.0, ["ojos", "visión", "vista"], "Especialista de los ojos"),
        ]
        
        for esp in especialidades:
            self.add_especialidad(*esp)
        
        # Planes de seguro
        planes = [
            ("plan_001", "Plan Básico", "Seguros XYZ", 60.0, 100.0, 15.0, "Cobertura básica"),
            ("plan_002", "Plan Plus", "Seguros XYZ", 80.0, 50.0, 10.0, "Cobertura intermedia"),
            ("plan_003", "Plan Premium", "Seguros XYZ", 95.0, 0.0, 5.0, "Cobertura completa"),
        ]
        
        for plan in planes:
            self.add_plan_seguro(*plan)
        
        # Cobertura por especialidad
        coberturas = [
            ("plan_001", "esp_001", 100.0, 15.0),
            ("plan_001", "esp_002", 60.0, 30.0),
            ("plan_001", "esp_003", 70.0, 20.0),
            ("plan_002", "esp_001", 100.0, 10.0),
            ("plan_002", "esp_002", 80.0, 20.0),
            ("plan_002", "esp_003", 90.0, 15.0),
            ("plan_003", "esp_001", 100.0, 5.0),
            ("plan_003", "esp_002", 100.0, 10.0),
            ("plan_003", "esp_003", 100.0, 10.0),
        ]
        
        for cob in coberturas:
            self.add_cobertura(*cob)
        
        print("[OK] Datos de ejemplo cargados")
    
    def get_coberturas_detalle(self) -> List[Dict]:
        """Obtener detalle de coberturas de especialidades por plan"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.nombre as plan_nombre, e.nombre as especialidad_nombre, 
                   c.cubre_porcentaje, c.copago_especialidad
            FROM cobertura_especialidad c
            JOIN planes_seguro p ON c.plan_id = p.id
            JOIN especialidades e ON c.especialidad_id = e.id
        """)
        coberturas = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return coberturas
    
    def clear_all(self):
        """Limpiar todas las tablas"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cobertura_especialidad")
        cursor.execute("DELETE FROM planes_seguro")
        cursor.execute("DELETE FROM especialidades")
        cursor.execute("DELETE FROM hospitales")
        conn.commit()
        conn.close()

```
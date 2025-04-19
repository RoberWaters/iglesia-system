import pyodbc
import os
from dotenv import load_dotenv
from typing import List, Tuple, Optional

load_dotenv()

class Database:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', 'localhost\\SQLEXPRESS')
        self.database = os.getenv('DB_NAME', 'IglesiaDB')
        self.username = os.getenv('DB_USER', 'sa')
        self.password = os.getenv('DB_PASSWORD', 'tu_contraseña')
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:
        """Establece conexión con la base de datos SQL Server"""
        try:
            self.conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                'TrustServerCertificate=yes;'
            )
            self.cursor = self.conn.cursor()
            return True
        except pyodbc.Error as e:
            print(f"Error de conexión: {e}")
            return False

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """Ejecuta una consulta que no retorna resultados"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error en consulta: {str(e)}")
            return False

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Tuple]]:
        """Ejecuta una consulta y retorna todos los resultados"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener datos: {str(e)}")
            return None

    def close(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_fieles(self) -> List[Tuple]:
        """Obtiene todos los fieles registrados según la estructura de la BD"""
        try:
            query = """
            SELECT 
                id_fiel, 
                nombre, 
                direccion, 
                telefono, 
                email 
            FROM Fieles 
            ORDER BY nombre
            """
            result = self.fetch_all(query)
            print("DEBUG - Resultado de get_fieles:", result)  # Para diagnóstico
            return result if result else []
        except Exception as e:
            print("Error crítico en get_fieles:", str(e))
            return []

    def add_fiel(self, nombre: str, direccion: str = None, telefono: str = None, email: str = None) -> bool:
        """Agrega un nuevo feligrés"""
        return self.execute_query(
            "INSERT INTO Fieles (nombre, direccion, telefono, email) VALUES (?, ?, ?, ?)",
            (nombre, direccion, telefono, email)
        )

    def get_sacramentos(self) -> List[Tuple]:
        """Obtiene todos los sacramentos con columnas explícitas"""
        try:
            query = """
            SELECT 
                id_sacramento, 
                nombre, 
                descripcion 
            FROM Sacramentos 
            ORDER BY nombre
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error en get_sacramentos: {e}")
            return []

    def add_sacramento(self, nombre: str, descripcion: str = None) -> bool:
        """Agrega un nuevo sacramento"""
        return self.execute_query(
            "INSERT INTO Sacramentos (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion)
        )

    def get_registros_sacramentales(self) -> List[Tuple]:
        """Obtiene registros sacramentales adaptado al esquema real"""
        try:
            query = """
            SELECT 
                rs.id_registro,
                f.nombre AS nombre_feligres,  
                s.nombre AS nombre_sacramento,
                rs.fecha,
                rs.sacerdote
            FROM Registros_Sacramentales rs
            JOIN Fieles f ON rs.id_fiel = f.id_fiel
            JOIN Sacramentos s ON rs.id_sacramento = s.id_sacramento
            ORDER BY rs.fecha DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error en get_registros_sacramentales: {e}")
            return []

    def add_registro_sacramental(self, id_fiel: int, id_sacramento: int, fecha: str, sacerdote: str) -> bool:
        """Agrega un nuevo registro sacramental"""
        return self.execute_query(
            "INSERT INTO Registros_Sacramentales (id_fiel, id_sacramento, fecha, sacerdote) VALUES (?, ?, ?, ?)",
            (id_fiel, id_sacramento, fecha, sacerdote)
        )

    def get_eventos(self) -> List[Tuple]:
        """Obtiene todos los eventos con columnas explícitas"""
        try:
            query = """
            SELECT 
                id_evento,
                titulo,
                descripcion,
                CONVERT(varchar, fecha, 120) AS fecha_formateada,
                lugar
            FROM Eventos 
            ORDER BY fecha DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error en get_eventos: {e}")
            return []

    def add_evento(self, titulo: str, descripcion: str, fecha: str, lugar: str) -> bool:
        """Agrega un nuevo evento"""
        return self.execute_query(
            "INSERT INTO Eventos (titulo, descripcion, fecha, lugar) VALUES (?, ?, ?, ?)",
            (titulo, descripcion, fecha, lugar)
        )

    # Métodos CRUD para Donaciones
    def get_donaciones(self) -> List[Tuple]:
        """Obtiene todas las donaciones"""
        return self.fetch_all("""
            SELECT d.id_donacion, f.nombre, d.monto, d.fecha, d.metodo_pago
            FROM Donaciones d
            JOIN Fieles f ON d.id_fiel = f.id_fiel
            ORDER BY d.fecha DESC
        """)

    def add_donacion(self, id_fiel: int, monto: float, fecha: str, metodo_pago: str) -> bool:
        """Agrega una nueva donación"""
        return self.execute_query(
            "INSERT INTO Donaciones (id_fiel, monto, fecha, metodo_pago) VALUES (?, ?, ?, ?)",
            (id_fiel, monto, fecha, metodo_pago)
        )

    def get_intenciones_misa(self) -> List[Tuple]:
        """Obtiene todas las intenciones de misa con formato correcto"""
        try:
            query = """
            SELECT 
                i.id_intencion, 
                f.nombre AS nombre_feligres, 
                i.descripcion, 
                CONVERT(varchar, i.fecha, 103) AS fecha_formateada
            FROM Intenciones_Misa i
            JOIN Fieles f ON i.id_fiel = f.id_fiel
            ORDER BY i.fecha DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error en get_intenciones_misa: {e}")
            return []
        

    def add_intencion_misa(self, id_fiel: int, descripcion: str, fecha: str) -> bool:
        """Agrega una nueva intención de misa"""
        return self.execute_query(
            "INSERT INTO Intenciones_Misa (id_fiel, descripcion, fecha) VALUES (?, ?, ?)",
            (id_fiel, descripcion, fecha)
        )
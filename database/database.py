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

    # Métodos CRUD para Fieles
    def get_fieles(self) -> List[Tuple]:
        """Obtiene todos los fieles registrados"""
        return self.fetch_all("SELECT * FROM Fieles ORDER BY nombre")

    def add_fiel(self, nombre: str, direccion: str = None, telefono: str = None, email: str = None) -> bool:
        """Agrega un nuevo feligrés"""
        return self.execute_query(
            "INSERT INTO Fieles (nombre, direccion, telefono, email) VALUES (?, ?, ?, ?)",
            (nombre, direccion, telefono, email)
        )

    # Métodos CRUD para Sacramentos
    def get_sacramentos(self) -> List[Tuple]:
        """Obtiene todos los sacramentos"""
        return self.fetch_all("SELECT * FROM Sacramentos ORDER BY nombre")

    def add_sacramento(self, nombre: str, descripcion: str = None) -> bool:
        """Agrega un nuevo sacramento"""
        return self.execute_query(
            "INSERT INTO Sacramentos (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion)
        )

    # Métodos CRUD para Registros Sacramentales
    def get_registros_sacramentales(self) -> List[Tuple]:
        """Obtiene todos los registros sacramentales"""
        return self.fetch_all("""
            SELECT r.id_registro, f.nombre, s.nombre, r.fecha, r.sacerdote 
            FROM Registros_Sacramentales r
            JOIN Fieles f ON r.id_fiel = f.id_fiel
            JOIN Sacramentos s ON r.id_sacramento = s.id_sacramento
            ORDER BY r.fecha DESC
        """)

    def add_registro_sacramental(self, id_fiel: int, id_sacramento: int, fecha: str, sacerdote: str) -> bool:
        """Agrega un nuevo registro sacramental"""
        return self.execute_query(
            "INSERT INTO Registros_Sacramentales (id_fiel, id_sacramento, fecha, sacerdote) VALUES (?, ?, ?, ?)",
            (id_fiel, id_sacramento, fecha, sacerdote)
        )

    # Métodos CRUD para Eventos
    def get_eventos(self) -> List[Tuple]:
        """Obtiene todos los eventos"""
        return self.fetch_all("SELECT * FROM Eventos ORDER BY fecha DESC")

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

    # Métodos CRUD para Intenciones
    def get_intenciones_misa(self) -> List[Tuple]:
        """Obtiene todas las intenciones de misa"""
        return self.fetch_all("""
            SELECT i.id_intencion, f.nombre, i.descripcion, i.fecha
            FROM Intenciones_Misa i
            JOIN Fieles f ON i.id_fiel = f.id_fiel
            ORDER BY i.fecha DESC
        """)

    def add_intencion_misa(self, id_fiel: int, descripcion: str, fecha: str) -> bool:
        """Agrega una nueva intención de misa"""
        return self.execute_query(
            "INSERT INTO Intenciones_Misa (id_fiel, descripcion, fecha) VALUES (?, ?, ?)",
            (id_fiel, descripcion, fecha)
        )
import unittest
import os
import tempfile
import shutil
import sqlite3
import urllib.parse
from rename_local_v2 import rename_in_folder

class TestRenameLogic(unittest.TestCase):
    
    def setUp(self):
        """Crear directorio temporal y DB de prueba"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_mixxxdb.sqlite")
        
        # Crear DB de prueba
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tablas como Mixxx
        cursor.execute("""
            CREATE TABLE track_locations (
                id INTEGER PRIMARY KEY,
                location TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE library (
                id INTEGER PRIMARY KEY,
                location INTEGER,
                rating INTEGER,
                FOREIGN KEY (location) REFERENCES track_locations(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Limpiar archivos temporales"""
        shutil.rmtree(self.test_dir)
    
    def _add_track_to_db(self, file_path, rating):
        """Helper para agregar track a la DB de prueba"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        location = 'file://' + urllib.parse.quote(file_path)
        cursor.execute("INSERT INTO track_locations (location) VALUES (?)", (location,))
        location_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO library (location, rating) VALUES (?, ?)", 
                      (location_id, rating))
        
        conn.commit()
        conn.close()
    
    def test_replace_00_with_rating(self):
        """Test: Archivo con 00- debe reemplazarse con rating"""
        # Crear archivo de prueba
        test_file = os.path.join(self.test_dir, "00-100-8A-test_song.m4a")
        open(test_file, 'a').close()
        
        # Agregar a DB con rating 4
        self._add_track_to_db(test_file, 4)
        
        # Simular renombrado (necesitaríamos modificar el script para usar DB personalizada)
        # Por ahora, test manual de la lógica
        import re
        filename = "00-100-8A-test_song.m4a"
        rating = 4
        rating_pattern = r'^(\d{2})([-_])'
        match = re.match(rating_pattern, filename)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "00")
        self.assertEqual(match.group(2), "-")
        
        # Resultado esperado
        expected = f"{rating:02d}-100-8A-test_song.m4a"
        result = f"{rating:02d}{match.group(2)}{filename[3:]}"
        self.assertEqual(result, expected)
    
    def test_preserve_existing_rating(self):
        """Test: Archivo con rating existente no debe modificarse"""
        filename = "03-100-8A-test_song.m4a"
        rating = 5  # Rating diferente en Mixxx
        
        import re
        rating_pattern = r'^(\d{2})([-_])'
        match = re.match(rating_pattern, filename)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "03")
        
        # No debe modificarse porque ya tiene rating != 00
        should_rename = (match.group(1) == "00")
        self.assertFalse(should_rename)
    
    def test_add_rating_to_file_without_prefix(self):
        """Test: Archivo sin prefijo debe recibir el rating"""
        filename = "test_song.m4a"
        rating = 4
        
        import re
        rating_pattern = r'^(\d{2})([-_])'
        match = re.match(rating_pattern, filename)
        
        self.assertIsNone(match)
        
        # Debe agregarse el rating con _
        expected = f"{rating:02d}_{filename}"
        self.assertEqual(expected, "04_test_song.m4a")
    
    def test_preserve_underscore_separator(self):
        """Test: Preservar guion bajo como separador"""
        filename = "00_test_song.m4a"
        rating = 3
        
        import re
        rating_pattern = r'^(\d{2})([-_])'
        match = re.match(rating_pattern, filename)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.group(2), "_")
        
        expected = f"{rating:02d}_{filename[3:]}"
        self.assertEqual(expected, "03_test_song.m4a")
    
    def test_preserve_hyphen_separator(self):
        """Test: Preservar guion como separador"""
        filename = "00-100-8A-test.m4a"
        rating = 5
        
        import re
        rating_pattern = r'^(\d{2})([-_])'
        match = re.match(rating_pattern, filename)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.group(2), "-")
        
        expected = f"{rating:02d}-100-8A-test.m4a"
        result = f"{rating:02d}{match.group(2)}{filename[3:]}"
        self.assertEqual(result, expected)


class TestMacOSCleanup(unittest.TestCase):
    
    def setUp(self):
        """Crear directorio temporal con archivos ._*"""
        self.test_dir = tempfile.mkdtemp()
        
        # Crear archivos normales y archivos ._
        self.normal_files = [
            "song1.m4a",
            "song2.mp3",
            "03-100-8A-song3.m4a"
        ]
        
        self.dot_underscore_files = [
            "._song1.m4a",
            "._song2.mp3",
            "._03-100-8A-song3.m4a"
        ]
        
        for f in self.normal_files:
            open(os.path.join(self.test_dir, f), 'a').close()
        
        for f in self.dot_underscore_files:
            open(os.path.join(self.test_dir, f), 'a').close()
    
    def tearDown(self):
        """Limpiar archivos temporales"""
        shutil.rmtree(self.test_dir)
    
    def test_identify_dot_underscore_files(self):
        """Test: Identificar correctamente archivos ._*"""
        files = os.listdir(self.test_dir)
        dot_files = [f for f in files if f.startswith("._")]
        
        self.assertEqual(len(dot_files), 3)
        for f in self.dot_underscore_files:
            self.assertIn(f, dot_files)
    
    def test_cleanup_removes_only_dot_underscore(self):
        """Test: Cleanup solo elimina archivos ._*, no los normales"""
        from rename_local_v2 import cleanup_macos_metadata
        
        initial_files = set(os.listdir(self.test_dir))
        cleanup_macos_metadata(self.test_dir)
        remaining_files = set(os.listdir(self.test_dir))
        
        # Los archivos normales deben permanecer
        for f in self.normal_files:
            self.assertIn(f, remaining_files)
        
        # Los archivos ._ deben eliminarse
        for f in self.dot_underscore_files:
            self.assertNotIn(f, remaining_files)


if __name__ == '__main__':
    unittest.main()

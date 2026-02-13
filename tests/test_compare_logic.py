import unittest
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

class TestCompareLogic(unittest.TestCase):
    def setUp(self):
        # Create a temporary in-memory DB or a test file
        self.test_db_path = "test_compare.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = DatabaseManager(self.test_db_path)
        
        # Insert dummy data into thuoc_generic
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        # Schema: stt, ten_thuoc, ten_hoat_chat, nong_do_ham_luong, gdklh, ... don_gia, nhom_thuoc
        # We need validation on 'ten_hoat_chat', 'nong_do_ham_luong', 'dang_bao_che', 'nhom_thuoc'
        
        # Insert 3 records: 2 matching, 1 non-matching
        # Rec 1: Paracetamol, 500mg, Vien nen, Nhom 1 - Price 100
        # Rec 2: Paracetamol, 500mg, Vien nen, Nhom 1 - Price 200
        # Rec 3: Paracetamol, 500mg, Vien sui, Nhom 1 - Price 300 (Diff form)
        
        # Columns in schema: ... ten_hoat_chat, nong_do_ham_luong, ... dang_bao_che ... don_gia ... nhom_thuoc
        
        sql = """
        INSERT INTO thuoc_generic (ten_hoat_chat, nong_do_ham_luong, dang_bao_che, nhom_thuoc, don_gia)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql, ("Paracetamol", "500mg", "Vien nen", "Nhom 1", "100"))
        cursor.execute(sql, ("Paracetamol", "500mg", "Vien nen", "Nhom 1", "200"))
        cursor.execute(sql, ("Paracetamol", "500mg", "Vien sui", "Nhom 1", "300"))
        
        # Insert dummy data into bhxh
        # Schema: stt, ten_thuoc, hoat_chat, ham_luong, dich_vu, ... gia, nhom_tckt
        # We need validation on 'hoat_chat', 'ham_luong', 'dang_bao_che', 'nhom_tckt', 'gia'
        
        sql_bhxh = """
        CREATE TABLE IF NOT EXISTS bhxh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hoat_chat TEXT,
            ham_luong TEXT,
            dang_bao_che TEXT,
            nhom_tckt TEXT,
            gia TEXT
        )
        """
        cursor.execute(sql_bhxh)
        
        sql_insert = "INSERT INTO bhxh (hoat_chat, ham_luong, dang_bao_che, nhom_tckt, gia) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql_insert, ("Metformin", "500mg", "Vien nen", "Nhom 1", "1000"))
        cursor.execute(sql_insert, ("Metformin", "500mg", "Vien nen", "Nhom 1", "1200"))
        
        conn.commit()
        conn.close()

    def tearDown(self):
        if hasattr(self, 'db'):
            del self.db
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass

    def test_get_price_statistics_bhxh(self):
        # Test Case 4: BHXH table (uses 'gia' column)
        criteria = {
            'hoat_chat': 'Metformin',
            'ham_luong': '500mg',
            'dang_bao_che': 'Vien nen',
            'nhom_tckt': 'Nhom 1'
        }
        stats = self.db.get_price_statistics("bhxh", criteria)
        
        self.assertEqual(stats['count'], 2)
        self.assertEqual(stats['min'], 1000)
        self.assertEqual(stats['max'], 1200)

    def test_get_price_statistics(self):
        # Test Case 1: Match 2 records
        criteria = {
            'ten_hoat_chat': 'Paracetamol',
            'nong_do_ham_luong': '500mg',
            'dang_bao_che': 'Vien nen',
            'nhom_thuoc': 'Nhom 1'
        }
        stats = self.db.get_price_statistics("thuoc_generic", criteria)
        
        self.assertEqual(stats['count'], 2)
        self.assertEqual(stats['min'], 100)
        self.assertEqual(stats['max'], 200)

    def test_get_price_statistics_no_match(self):
        # Test Case 2: No match
        criteria = {
            'ten_hoat_chat': 'Ibuprofen',
            'nong_do_ham_luong': '500mg'
        }
        stats = self.db.get_price_statistics("thuoc_generic", criteria)
        self.assertEqual(stats['count'], 0)
        self.assertEqual(stats['min'], 0)
        self.assertEqual(stats['max'], 0)
        
    def test_case_insensitive(self):
        # Test Case 3: Case insensitive match
        criteria = {
            'ten_hoat_chat': 'paracetamol', # lowercase
            'nong_do_ham_luong': '500mg'
        }
        # Note: current implementation uses LOWER() so it should match all 3 if we don't filter by form
        stats = self.db.get_price_statistics("thuoc_generic", criteria)
        self.assertEqual(stats['count'], 3) 
        self.assertEqual(stats['min'], 100)
        self.assertEqual(stats['max'], 300)

if __name__ == '__main__':
    unittest.main()

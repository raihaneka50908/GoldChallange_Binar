import sqlite3

# terhubung ke database
conn = sqlite3.connect('Database_Challange.db')

# membuat kursor untuk mengirim perintah SQL
cursor = conn.cursor()

# melakukan perintah SELECT untuk memilih semua isi tabel 'nama_tabel'
cursor.execute("SELECT * FROM Kata_Kata")

# mendapatkan semua baris hasil query
rows = cursor.fetchall()

# print setiap baris
for row in rows:
    print(row)

# menutup koneksi
conn.close()
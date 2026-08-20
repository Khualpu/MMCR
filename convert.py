import sqlite3
import xml.etree.ElementTree as ET

# 1. Connect to / create SQLite database
conn = sqlite3.connect("bible.sqlite")
cursor = conn.cursor()

# 2. Set page size to match HTTP Range requests and create table
cursor.execute("PRAGMA page_size = 1024;")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS bible (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_number INTEGER,
        chapter_number INTEGER,
        verse_number INTEGER,
        text TEXT
    )
"""
)

# 3. Parse XML file
tree = ET.parse("NTB.xml")
root = tree.getroot()

# 4. Extract data and insert into database
rows = []
for book in root.findall("book"):
    book_num = int(book.get("number"))
    for chapter in book.findall("chapter"):
        chap_num = int(chapter.get("number"))
        for verse in chapter.findall("verse"):
            verse_num = int(verse.get("number"))
            verse_text = verse.text.strip() if verse.text else ""
            rows.append((book_num, chap_num, verse_num, verse_text))

cursor.executemany(
    """
    INSERT INTO bible (book_number, chapter_number, verse_number, text)
    VALUES (?, ?, ?, ?)
""",
    rows,
)

# 5. Create index for fast GitHub HTTP Range queries
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_bible_lookup ON bible(book_number, chapter_number, verse_number, text);"
)

# 6. Commit insertion operations first
conn.commit()

# 7. Optimize settings after committing
cursor.execute("PRAGMA journal_mode = DELETE;")
cursor.execute("VACUUM;")

conn.close()
print("Successfully created optimized bible.sqlite!")
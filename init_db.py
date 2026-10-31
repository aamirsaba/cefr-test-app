import sqlite3
import hashlib

DB_PATH = "cefr_test.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
        center TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, user_name TEXT NOT NULL,
        user_email TEXT NOT NULL, user_phone TEXT NOT NULL, center TEXT NOT NULL,
        total_score INTEGER NOT NULL, cefr_level TEXT NOT NULL, module_assigned TEXT NOT NULL,
        section1_score INTEGER, section2_score INTEGER, section3_score INTEGER, section4_score INTEGER,
        answers TEXT, enrolled INTEGER DEFAULT 0, started_at TIMESTAMP, time_taken_seconds INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, full_name TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY, section INTEGER NOT NULL, question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL, option_a TEXT NOT NULL, option_b TEXT NOT NULL,
        option_c TEXT NOT NULL, option_d TEXT NOT NULL, correct_answer TEXT NOT NULL, cefr_level TEXT NOT NULL)""")

    # Admin setup
    admin_email = "aamir.durrani@kg.om"
    if not c.execute("SELECT id FROM admins WHERE email=?", (admin_email,)).fetchone():
        c.execute("INSERT INTO admins (email, password_hash, full_name) VALUES (?, ?, ?)",
                  (admin_email, hash_password("Allahis1!"), "Aamir Durrani"))

    c.execute("DELETE FROM questions")
    
    ar_questions = [
        (1, 1, 1, "____ مُهَنْدِسَةٌ في الشَّرِكَة.", "هُوَ", "هِيَ", "أَنْتَ", "نَحْنُ", "B", "A1"),
        (2, 1, 2, "السَّلامُ عَلَيْكُـمْ! وَعَلَيْكُمُ السَّلام، كَيْفَ ____؟", "اسْمُكَ", "عَمَلُكَ", "حَالُكَ", "بَلَدُكَ", "C", "A1"),
        (3, 1, 3, "____ طَالِبٌ نَشيطٌ في المَعْهَد.", "هَذَا", "هَذِهِ", "هَؤُلاءِ", "تِلْكَ", "A", "A1"),
        (4, 1, 4, "اختر الرقم الصحيح لـ (25):", "خَمْسَةٌ وعِشْرُونَ", "عِشْرُونَ وخَمْسَة", "خَمْسَةٌ وعَشَرَة", "خَمْسَة وعِشْرينَ", "A", "A1"),
        (5, 1, 5, "يَسْكُنُ المُديرُ ____ المَدينَةِ.", "عَلى", "إلى", "في", "عَنْ", "C", "A1"),
        (6, 1, 6, "اختر ضمير الملكية الصحيح لـ 'مكتبنا': مَكْتَبُ ____", "مَكْتَبُكَ", "مَكْتَبُهُ", "مَكْتَبُنَا", "مَكْتَبُهُمْ", "C", "A1"),
        (7, 2, 7, "أَمْسِ، ____ إلَى المَكْتَبِ مُبَكِّرًا.", "ذَهَبَ", "ذَهَبْتُ", "ذَهَبَتْ", "نَذْهَبُ", "B", "A2"),
        (8, 2, 8, "____ المُهَنْدِسُ اليَوْمَ إلَى العَمَلِ بِسَبَبِ المَرَض.", "لَمْ يَحْضُرْ", "لَنْ يَحْضُرَ", "مَا يَحْضُرُ", "لَا يَحْضُرُ", "D", "A2"),
        (9, 2, 9, "قَرَأْتُ رِسَالَةً ____ مِنْ الشَّرِكَة.", "جَديدٌ", "جَديدَةً", "جَديدَةٌ", "جَديدِ", "B", "A2"),
        (10, 2, 10, "يَبْدَأُ الِاجْتِماعُ فِي السَّاعَةِ ____.", "التَّاسِعَةِ", "تِسْعَة", "التَّاسِع", "تِسْع", "A", "A2"),
        (11, 2, 11, "الشَّرِكَةُ الجَديدَةُ أَكْبَرُ ____ القَديمَة.", "مِنْ", "عَلى", "في", "بـِ", "A", "A2"),
        (12, 2, 12, "كُلَّ يَوْمٍ، ____ الصَّباحِيَّ فِي المَكْتَب.", "أَكْتُبُ التَّقْريرَ", "كَتَبْتُ التَّقْريرَ", "سَأَكْتُبُ التَّقْريرَ", "أَكْتَبَ التَّقْريرَ", "A", "A2"),
        (13, 3, 13, "وَجَدْتُ ____ الشَّرِكَةِ عَلى المَكْتَب.", "مِلَفُّ", "مِلَفَّ", "مِلَفِّ", "مِلَفٌّ", "C", "B1"),
        (14, 3, 14, "____ المُديرُ سِيرَةً ذَاتِيَّةً جَديدَةً غَدًا.", "يُقَدِّمُ", "سَيُقَدِّمُ", "قَدَّمَ", "قَدَّمُوا", "B", "B1"),
        (15, 3, 15, "____ صُعوبَةِ المَشْرُوعِ، نَجَحَ الفَرِيقُ في إِتْمامِه.", "بِرَغْمِ", "عَلَى الرَّغْمِ مِنْ أَنَّ", "لِكَيْ", "حَتَّى", "B", "B1"),
        (16, 3, 16, "____ المُهَنْدِسُ التَّقْريرَ الفَنِّيَّ في وَقْتِهِ.", "أَتَمَّ", "تَتَمَّ", "اسْتَتَمَّ", "تَمَّ", "A", "B2"),
        (17, 3, 17, "تُركِزُ الشَّرِكَةُ عَلى تَطْويرِ مَهاراتِ العامِلينَ... ما هو مِحْوَرُ تَرْكيزِ الشَّرِكَة؟", "بِنَاءُ المَكاتِبِ", "تَطْويرُ مَهاراتِ العامِلينَ", "إيقافُ بَرامِجِ التَّدريب", "تخْفيضُ العَامِلينَ", "B", "B2"),
        (18, 3, 18, "اِجْتَمَعْنَا اليَوْمَ ____ مُناقَشَةِ الخُطَّةِ الِاسْتِراتيجِيَّة.", "مِنْ أَجْلِ", "بَلْ", "أَوْ", "ثُمَّ", "A", "B2"),
        (19, 3, 19, "____ المَشْرُوعُ الجَديدُ رَسْمِيًّا الأسبوعَ الماضِي.", "اُفْتُتِحَ", "فَتَحَ", "يَفْتَتِحُ", "افْتَتَحَ", "A", "B2"),
        (20, 4, 20, "حَضَرَ جَميعُ المُهَنْدِسينَ الإجْتماعَ إِلَّا ____ واحِدًا.", "مُهَنْدِسٌ", "مُهَنْدِسًا", "مُهَنْدِسٍ", "الـمُهَنْدِسُ", "B", "C1"),
        (21, 4, 21, "تَعْمَلُ الإدارَةُ العُليا عَلى ____ سِياساتٍ تَنْظيمِيَّةٍ جَديدَة.", "صِياغَةِ", "أَكْلِ", "نَوْمِ", "لَعِبِ", "A", "C1"),
        (22, 4, 22, "____ تَجْتَهِدْ في عَمَلِكَ، تَنْجَحْ.", "إِنْ", "لَوْ", "لَمَّا", "كَيْفَ", "A", "C2"),
        (23, 4, 23, "انْتَشَرَتِ التَّكْنُولُوجْيا الحَديثَةُ ____ واسِعًا.", "انْتِشارًا", "انْتِشارُ", "انْتِشارٍ", "يَنْتَشِرُ", "A", "C2"),
        (24, 4, 24, "تُعَدُّ وثيقَةُ ____ المُرْشِدَ الرَّئِيسيَّ لِتَفادي الأَخْطاءِ التَّنْفيذِيَّة.", "المُحاسَبَةِ", "المُغامَرَةِ", "المُنافَسَةِ", "المُواجَهَةِ", "A", "C2"),
        (25, 4, 25, "ما نوع الأسلوب في قوله تعالي: {فَلَا تَقُلْ لَهُمَا أُفٍّ}؟", "أسلوب نهي", "أسلوب استفهام", "أسلوب تعجب", "أسلوب أمر", "A", "C2"),
    ]

    c.executemany("""INSERT INTO questions (id, section, question_number, question_text,
        option_a, option_b, option_c, option_d, correct_answer, cefr_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", ar_questions)

    conn.commit()
    conn.close()
    print("✅ Arabic database initialized!")

if __name__ == "__main__":
    init_db()
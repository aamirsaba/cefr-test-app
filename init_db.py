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
        section1_score INTEGER, section2_score INTEGER, section3_score INTEGER,
        answers TEXT, enrolled INTEGER DEFAULT 0, started_at TIMESTAMP, time_taken_seconds INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, full_name TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY, section INTEGER NOT NULL, question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL, option_a TEXT NOT NULL, option_b TEXT NOT NULL,
        option_c TEXT NOT NULL, option_d TEXT NOT NULL, correct_answer TEXT NOT NULL)""")

    # Admin setup
    admin_email = "aamir.durrani@kg.om"
    if not c.execute("SELECT id FROM admins WHERE email=?", (admin_email,)).fetchone():
        c.execute("INSERT INTO admins (email, password_hash, full_name) VALUES (?, ?, ?)",
                  (admin_email, hash_password("Allahis1!"), "Aamir Durrani"))

    c.execute("DELETE FROM questions")
    
    # 50 ENGLISH QUESTIONS
    en_questions = [
        (1, 1, 1, "Hello, my name _____ Sara.", "am", "is", "are", "be", "B"),
        (2, 1, 2, "Where _____ you from?", "do", "are", "is", "come", "B"),
        (3, 1, 3, "They _____ live in a big house; they live in a small apartment.", "isn't", "doesn't", "don't", "aren't", "C"),
        (4, 1, 4, "What time _____ your brother usually go to work?", "do", "is", "does", "has", "C"),
        (5, 1, 5, "I haven't got _____ free time today.", "many", "some", "much", "an", "C"),
        (6, 1, 6, "Look at _____ shoes over there near the door.", "this", "that", "these", "those", "D"),
        (7, 1, 7, "What time did you _____ at the office yesterday?", "arrived", "arrive", "arriving", "arrives", "B"),
        (8, 1, 8, "She is much _____ than her sister.", "tall", "taller", "more tall", "tallest", "B"),
        (9, 1, 9, "We _____ to Dubai last summer on holiday.", "go", "went", "gone", "have gone", "B"),
        (10, 1, 10, "Excuse me, is there a bank _____ to the supermarket?", "next", "opposite", "behind", "near", "A"),
        (11, 1, 11, "What _____ you doing yesterday at 5 PM?", "were", "was", "are", "did", "A"),
        (12, 1, 12, "I _____ to visit my uncle next weekend.", "go", "am going", "went", "gone", "B"),
        (13, 1, 13, "You _____ wear a seatbelt while driving. It's the law.", "should", "must", "can", "might", "B"),
        (14, 1, 14, "This is the _____ movie I have ever seen!", "good", "better", "best", "most good", "C"),
        (15, 1, 15, "Can you help _____ with this box, please?", "I", "my", "me", "mine", "C"),
        (16, 2, 16, "I have lived in Muscat _____ three years.", "since", "for", "during", "from", "B"),
        (17, 2, 17, "She has _____ finished her homework, so she can go out.", "yet", "already", "ever", "never", "B"),
        (18, 2, 18, "If it rains tomorrow, we _____ stay at home.", "would", "will", "had", "did", "B"),
        (19, 2, 19, "The new hospital _____ built by the government last year.", "is", "has been", "was", "were", "C"),
        (20, 2, 20, "My manager asked me where I _____ the project files.", "put", "have put", "had put", "am putting", "C"),
        (21, 2, 21, "If I _____ more time, I would learn a third language.", "have", "had", "will have", "would have", "B"),
        (22, 2, 22, "You _____ brought an umbrella; it didn't rain at all.", "needn't have", "shouldn't", "mustn't", "couldn't", "A"),
        (23, 2, 23, "The man _____ sitting near the door is our chief engineer.", "who", "which", "whose", "whom", "A"),
        (24, 2, 24, "We are looking forward to _____ you next week.", "meet", "meeting", "met", "have met", "B"),
        (25, 2, 25, "I don't mind _____ late if we need to finish the deadline.", "work", "to work", "working", "worked", "C"),
        (26, 2, 26, "He asked me how long _____ English.", "I had been studying", "had I studied", "I am studying", "have I studied", "A"),
        (27, 2, 27, "Car prices have increased significantly, _____ fewer people are buying new vehicles.", "although", "so", "because", "despite", "B"),
        (28, 2, 28, "By the time we reached the station, the train _____.", "left", "has left", "had left", "leaves", "C"),
        (29, 2, 29, "She gave me a very useful piece of _____.", "advice", "advices", "advising", "advised", "A"),
        (30, 2, 30, "Do you know where _____?", "is the office", "the office is", "was the office", "the office was located", "B"),
        (31, 2, 31, "They _____ to Paris three times this year.", "went", "have been", "had gone", "go", "B"),
        (32, 2, 32, "He spoke so fast that I could _____ understand what he said.", "hard", "hardly", "harder", "hardest", "B"),
        (33, 2, 33, "You should _____ your car serviced before taking a long travel trip.", "get", "make", "do", "let", "A"),
        (34, 2, 34, "_____ it was raining heavily, they continued the outdoor football match.", "Despite", "Although", "However", "In spite of", "B"),
        (35, 2, 35, "The meeting has been postponed _____ next Tuesday.", "until", "for", "since", "on", "A"),
        (36, 3, 36, "If I had known about the traffic jam, I _____ earlier.", "left", "would leave", "would have left", "will have left", "C"),
        (37, 3, 37, "Seldom _____ such an inspiring presentation on workplace AI.", "I have heard", "have I heard", "I heard", "did I heard", "B"),
        (38, 3, 38, "_____ completed the financial audit, the auditor submitted the final report.", "Having", "After", "On", "While", "A"),
        (39, 3, 39, "The company CEO insisted that the report _____ submitted by 5:00 PM.", "is", "be", "will be", "was", "B"),
        (40, 3, 40, "Had I realized the cost involved, I _____ approved the budget proposal.", "won't have", "wouldn't have", "haven't", "couldn't", "B"),
        (41, 3, 41, "It is high time we _____ updating our regional branch IT infrastructure.", "start", "started", "have started", "will start", "C"),
        (42, 3, 42, "Neither the regional director nor his assistants _____ available for comment.", "was", "were", "is", "have", "B"),
        (43, 3, 43, "The proposal was rejected on the _____ that it lacked proper financial details.", "grounds", "reason", "cause", "purpose", "C"),
        (44, 3, 44, "No sooner _____ the building than it began to rain heavily.", "we had left", "had we left", "did we leave", "we left", "C"),
        (45, 3, 45, "You can borrow the equipment, _____ you return it in good condition by Friday.", "as far as", "provided that", "unless", "in case", "B"),
        (46, 3, 46, "He speaks English with such confidence that he is often mistaken _____ a native speaker.", "by", "as", "for", "with", "C"),
        (47, 3, 47, "The team succeeded in completing the project _____ facing severe logistical delays.", "although", "despite", "even though", "whereas", "C"),
        (48, 3, 48, "What surprised me most _____ his complete lack of interest in the business negotiation.", "is", "were", "was", "are", "C"),
        (49, 3, 49, "Under no circumstances _____ leave confidential student files unattended.", "you should", "should you", "you must", "you can", "B"),
        (50, 3, 50, "The training program will help you get used to _____ complex datasets efficiently.", "handle", "handling", "handled", "be handled", "B"),
    ]

    c.executemany("""INSERT INTO questions (id, section, question_number, question_text,
        option_a, option_b, option_c, option_d, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", en_questions)

    conn.commit()
    conn.close()
    print("✅ English database initialized with 50 questions!")

if __name__ == "__main__":
    init_db()
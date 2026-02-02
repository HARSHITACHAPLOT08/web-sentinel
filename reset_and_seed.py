from database.db_manager import DBManager
from database.models import Website, CheckLog, AlertLog

def reset_and_seed():
    db = DBManager()
    
    # Reset existing data
    with db.get_session() as session:
        print("Cleaning up existing data...")
        session.query(CheckLog).delete()
        session.query(AlertLog).delete()
        session.query(Website).delete()
    
    sites = [
        # Current Affairs (Daily, India/Exam-Focused)
        ("GKToday - SSC/UPSC", "https://www.gktoday.in/"),
        ("Drishti IAS - News Analysis", "https://www.drishtiias.com/current-affairs-news-analysis-editorials"),
        ("AffairsCloud - Quizzes/PDFs", "https://affairscloud.com/"),
        ("Adda247 - SSC/Banking", "https://currentaffairs.adda247.com/"),
        ("PW Live - SSC/Railway", "https://www.pw.live/ssc/exams/daily-current-affairs-today"),
        
        # Python Programming (News & Updates)
        ("Python.org Blogs", "https://www.python.org/blogs"),
        ("Python Weekly", "https://www.pythonweekly.com/"),
        ("Real Python News", "https://realpython.com/tutorials/news"),
        
        # Cybersecurity (Daily News)
        ("The Hacker News", "https://thehackernews.com/"),
        ("Dark Reading", "https://www.darkreading.com/"),
        ("Security Week", "https://www.securityweek.com/"),
        
        # Python Automation (Scripts)
        ("Automate the Boring Stuff", "https://automatetheboringstuff.com/"),
        ("Real Python - Automation", "https://realpython.com/"),
        
        # SSC CGL Exam (Official/Prep)
        ("SSC Official Site", "https://ssc.gov.in/"),
        ("Testbook - SSC CGL", "https://testbook.com/ssc-cgl-exam"),
        ("Oliveboard - SSC CGL", "https://www.oliveboard.in/ssc-cgl"),
        
        # General/Additional
        ("Google", "https://www.google.com/"),
        ("YouTube", "https://www.youtube.com/"),
        ("MyGov India", "https://www.mygov.in/"),
        ("Microsoft IT", "https://www.microsoft.com/"),
        
        # General Technology News & Emerging Tech Updates
        ("TechCrunch", "https://techcrunch.com/"),
        ("Wired", "https://www.wired.com/"),
        ("The Verge", "https://www.theverge.com/"),
        ("MIT Technology Review", "https://www.technologyreview.com/"),
        ("Engadget", "https://www.engadget.com/"),
        ("Ars Technica", "https://arstechnica.com/"),
        
        # Specialized Tech Update Sites
        ("VentureBeat", "https://venturebeat.com/"),
        ("Digital Trends", "https://www.digitaltrends.com/"),
        ("Reuters Technology", "https://www.reuters.com/technology"),
        
        # IT Companies (Consulting/Services)
        ("WEBaniX Solutions", "https://webanixsolutions.com/"),
        ("PHP Poets Solutions", "https://phppoets.com/"),
        ("Zenver Technologies", "https://www.zenver.in/"),
    ]
    
    print(f"Seeding {len(sites)} categorized websites...")
    for name, url in sites:
        try:
            db.add_website(name, url, 300) # Setting default interval to 5 mins for bulk
            print(f" [+] Added: {name}")
        except Exception as e:
            print(f" [!] Error adding {name}: {e}")
            
    print("\nDatabase reset and seeded successfully.")
    print("Restart your background monitor script to start tracking these sites!")

if __name__ == "__main__":
    reset_and_seed()

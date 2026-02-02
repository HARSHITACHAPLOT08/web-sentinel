from database.db_manager import DBManager

def bulk_add():
    db = DBManager()
    sites = [
        # Current Affairs
        ("GKToday", "https://www.gktoday.in/"),
        ("Drishti IAS", "https://www.drishtiias.com/current-affairs-news-analysis-editorials"),
        ("AffairsCloud", "https://affairscloud.com/"),
        ("Adda247", "https://currentaffairs.adda247.com/"),
        ("PW Live SSC", "https://www.pw.live/ssc/exams/daily-current-affairs-today"),
        
        # Python Programming
        ("Python Blogs", "https://www.python.org/blogs"),
        ("Python Weekly", "https://www.pythonweekly.com/"),
        ("Real Python News", "https://realpython.com/tutorials/news"),
        
        # Cybersecurity
        ("The Hacker News", "https://thehackernews.com/"),
        ("Dark Reading", "https://www.darkreading.com/"),
        ("Security Week", "https://www.securityweek.com/"),
        
        # Python Automation
        ("Automate the Boring Stuff", "https://automatetheboringstuff.com/"),
        ("Real Python Tutorials", "https://realpython.com/"),
        
        # SSC CGL
        ("SSC Official", "https://ssc.gov.in/"),
        ("Testbook SSC", "https://testbook.com/ssc-cgl-exam"),
        ("Oliveboard SSC", "https://www.oliveboard.in/ssc-cgl"),
        
        # General
        ("Google", "https://www.google.com/"),
        ("YouTube", "https://www.youtube.com/"),
        ("MyGov India", "https://www.mygov.in/"),
        ("Microsoft", "https://www.microsoft.com/"),
        
        # IT Companies
        ("Webanix Solutions", "https://webanixsolutions.com/"),
        ("PHP Poets", "https://phppoets.com/"),
        ("Zenver Technologies", "https://www.zenver.in/"),
    ]
    
    print(f"Starting bulk add of {len(sites)} websites...")
    added_count = 0
    error_count = 0
    
    for name, url in sites:
        try:
            # Using default interval of 60s for all
            db.add_website(name, url, 60)
            print(f" [+] Added: {name}")
            added_count += 1
        except Exception as e:
            # Likely unique constraint if already exists
            print(f" [!] Skip/Error {name}: {e}")
            error_count += 1
            
    print(f"\nFinished. Added: {added_count}, Skipped/Errors: {error_count}")
    print("Note: Restart the background monitor to start tracking new sites.")

if __name__ == "__main__":
    bulk_add()

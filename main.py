from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re

print("="*65)
print("  HELSINKI NEW RESTAURANTS - FINAL VERSION")
print("  Criteria: Opened September 2025 - January 2026")
print("  High quality (4.0+ rating), No chains, No bars")
print("="*65)

# Exclude chains, hotels, bars, and known OLD restaurants
EXCLUDE = [
    # Chains
    "friends & brgrs", "hesburger", "mcdonalds", "burger king", 
    "subway", "kotipizza", "starbucks", "espresso house", "fafa",
    "rax", "rosso", "amarillo", "hanko sushi", "vapiano",
    # Hotels
    "kämp", "kamp", "hotel", "hotelli", "scandic", "hilton", "radisson", "sokos",
    # Bars
    "bar", "baari", "pub", "club", "social club",
    # Known OLD restaurants
    "nokka", "olo", "grön", "savoy", "palace",
    "onigiri musubi", "bona fide", "canvas canteen", "nolita",
    "baskeri", "kuurna", "elm", "blondie", "aoi", "maukku", "forza", "teller",
    "kosmos", "boulevard bar", "demo", "ask", "ora", "finnjävel"
]

options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(3)

all_urls = set()

# Comprehensive searches - restaurants only, no bars
searches = [
    # Specific new restaurants
    "esmes helsinki",
    "esmes ravintola",
    
    # Time-specific
    "new restaurant helsinki 2025",
    "uusi ravintola helsinki 2025",
    "new restaurant helsinki september 2025",
    "new restaurant helsinki october 2025",
    "new restaurant helsinki november 2025",
    "new restaurant helsinki december 2025",
    "ravintola avattu helsinki 2025",
    
    # Area-specific
    "uusi ravintola töölö",
    "uusi ravintola rödbergen",
    "uusi ravintola kallio",
    "uusi ravintola punavuori",
    "uusi ravintola kruununhaka",
    "uusi ravintola kamppi",
    "uusi ravintola ullanlinna",
    "uusi ravintola sörnäinen",
    "uusi ravintola katajanokka",
    
    # Type-specific (no bars)
    "new fine dining helsinki 2025",
    "new bistro helsinki 2025",
    "uusi lounas ravintola helsinki",
    "new italian restaurant helsinki",
    "new asian restaurant helsinki",
    "new nordic restaurant helsinki",
    
    # Finnish
    "ravintola avajaiset helsinki 2025",
    "uudet ravintolat helsinki"
]

print(f"\nRunning {len(searches)} searches...")

for search in searches:
    print(f"  {search}")
    driver.get(f"https://www.google.com/maps/search/{search.replace(' ', '+')}")
    time.sleep(3)
    
    for _ in range(5):
        try:
            feed = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
            time.sleep(1.5)
        except:
            pass
    
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
    for l in links:
        href = l.get_attribute("href")
        if href:
            all_urls.add(href)

print(f"\nFound {len(all_urls)} unique places to check")
print("="*65)

results = []

for i, url in enumerate(list(all_urls)):
    try:
        driver.get(url)
        time.sleep(2)
        
        # Get name
        try:
            name = driver.find_element(By.CSS_SELECTOR, "h1").text
        except:
            continue
        
        # Skip excluded (including bars)
        name_lower = name.lower()
        if any(ex in name_lower for ex in EXCLUDE):
            continue
        
        # Get place type and skip bars
        try:
            place_type = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category']").text.lower()
            if 'bar' in place_type or 'pub' in place_type or 'club' in place_type:
                continue
        except:
            pass
        
        # Get rating
        rating = ""
        rating_num = 0
        try:
            rating = driver.find_element(By.CSS_SELECTOR, "div.F7nice span").text
            rating_num = float(rating.replace(",", "."))
        except:
            pass
        
        # Skip low ratings
        if rating_num > 0 and rating_num < 4.0:
            continue
        
        # Get review count
        review_count = 0
        try:
            spans = driver.find_elements(By.CSS_SELECTOR, "span")
            for span in spans:
                text = span.text
                if "review" in text.lower() or "recension" in text.lower():
                    nums = re.findall(r'\d+', text.replace(',', '').replace(' ', ''))
                    if nums:
                        review_count = int(nums[0])
                        break
        except:
            pass
        
        # Skip if too many reviews (not new)
        if review_count > 500:
            continue
        
        # Click reviews tab
        has_owner_response = False
        oldest_review = ""
        is_truly_new = False
        
        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
            for tab in tabs:
                label = tab.get_attribute("aria-label") or ""
                if 'review' in label.lower() or 'recension' in label.lower():
                    tab.click()
                    time.sleep(2)
                    break
            
            # Check for owner responses
            page_text = driver.page_source.lower()
            if 'response from' in page_text or 'svar från' in page_text:
                has_owner_response = True
            
            # Sort by oldest
            try:
                sort_btn = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Sort']")
                if sort_btn:
                    sort_btn[0].click()
                    time.sleep(1)
                    
                    menu_items = driver.find_elements(By.CSS_SELECTOR, "div[role='menuitemradio']")
                    for item in menu_items:
                        if 'oldest' in item.text.lower() or 'äldst' in item.text.lower():
                            item.click()
                            time.sleep(2)
                            break
                    
                    dates = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
                    if dates:
                        oldest_review = dates[-1].text
            except:
                pass
        except:
            pass
        
        # Check if TRULY new (opened Sep 2025+ = max 5 months ago)
        if oldest_review:
            oldest_lower = oldest_review.lower()
            if 'week' in oldest_lower or 'vecka' in oldest_lower:
                is_truly_new = True
            elif 'day' in oldest_lower or 'dag' in oldest_lower:
                is_truly_new = True
            elif 'month' in oldest_lower or 'månad' in oldest_lower:
                nums = re.findall(r'\d+', oldest_review)
                if nums and int(nums[0]) <= 5:
                    is_truly_new = True
            elif oldest_lower.startswith('a month') or oldest_lower.startswith('en månad'):
                is_truly_new = True
        
        if is_truly_new:
            owner = "✓" if has_owner_response else ""
            print(f"✓ {name} | {rating} ({review_count}) | {oldest_review} | Owner:{owner}")
            
            results.append({
                'name': name,
                'rating': rating,
                'reviews': review_count,
                'has_owner_response': has_owner_response,
                'oldest_review': oldest_review,
                'url': url
            })
        
    except:
        pass

driver.quit()

# Sort by rating
results.sort(key=lambda x: float(x['rating'].replace(',', '.')) if x['rating'] else 0, reverse=True)

print("\n" + "="*65)
print("🍽️  NEW HELSINKI RESTAURANTS (Sep 2025 - Jan 2026)")
print("="*65)

if results:
    for i, r in enumerate(results):
        owner = "✓" if r['has_owner_response'] else ""
        print(f"\n{i+1}. {r['name']}")
        print(f"   ⭐ {r['rating']} ({r['reviews']} reviews)")
        print(f"   📅 First review: {r['oldest_review']}")
        print(f"   👨‍🍳 Owner responds: {owner}")
else:
    print("No new restaurants found")

# Save
with open("helsinki_new_restaurants_final.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "rating", "reviews", "has_owner_response", "oldest_review", "url"])
    w.writeheader()
    w.writerows(results)

print(f"\n" + "="*65)
print(f"TOTAL: {len(results)} new restaurants found")
print("Saved to helsinki_new_restaurants_final.csv")
print("="*65)

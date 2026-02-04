# Case 1: New Restaurant Discovery - Process Document

## The Challenge

Find all new restaurant openings in Helsinki between September 2025 and January 2026 that meet World of Mouth (WoM) quality standards.

## The Problem

**There is no API or database that tracks restaurant opening dates.**

- Google Places API has no "opening date" field
- Google Maps doesn't expose when a business was added
- Finnish restaurant news is scattered across multiple sources

## Approaches Tested

### 1. Google Places API Only ❌
- **Attempt:** Search for restaurants and filter by low review count
- **Problem:** Low reviews ≠ new restaurant (could just be unpopular)
- **Result:** Many false positives (established restaurants with few reviews)

### 2. News Scraping (City.fi) ❌
- **Attempt:** Scrape Finnish restaurant news for "new opening" articles
- **Problem:** Articles don't consistently mention opening dates
- **Result:** Only found 3 restaurants, missed many others

### 3. Gemini AI Direct Query ❌
- **Attempt:** Ask Gemini to list new Helsinki restaurants
- **Problem:** AI hallucinated fake restaurant names
- **Result:** Completely unreliable data

### 4. Selenium + Review Date Analysis ✅
- **Attempt:** Use browser automation to check each restaurant's oldest review
- **Logic:** If the oldest review is from Sep 2025 or later → restaurant is new
- **Result:** Successfully identified genuinely new restaurants

## Final Solution

**Selenium-based scraper that:**

1. Searches Google Maps with multiple queries:
   - "uusi ravintola helsinki 2025"
   - "new restaurant helsinki october 2025"
   - Area-specific searches (Kallio, Punavuori, Töölö, etc.)

2. For each restaurant found:
   - Opens the Google Maps page
   - Clicks on Reviews tab
   - Sorts reviews by "Oldest"
   - Extracts the oldest review date

3. Filters restaurants where:
   - Oldest review ≤ 5 months ago (= opened Sep 2025+)
   - Rating ≥ 4.0
   - Not a chain restaurant
   - Not a bar/club
   - Not an already-known WoM restaurant

4. Additional quality signals:
   - Owner responds to reviews (indicates engaged management)
   - Review count < 150 (very new places can't have thousands of reviews)

## Challenges Overcome

### Challenge 1: Esmes Not Found Initially
- **Problem:** Searched for "esme" but restaurant is named "Esmes"
- **Solution:** Added specific search terms and manual verification

### Challenge 2: False Positives (Old Restaurants)
- **Problem:** Some established restaurants showed recent "oldest review" dates
- **Cause:** Google may have lost/reset old review data
- **Solution:** Added review count filter (>500 reviews = definitely not new)

### Challenge 3: API Key in Git
- **Problem:** GitHub blocked push due to exposed API key
- **Solution:** Reset git history and added config.py to .gitignore

## WoM Quality Criteria Applied

Restaurants were evaluated against WoM standards:
- ✅ Owner-operated or chef-driven
- ✅ Unique concept (not generic)
- ✅ Quality-focused
- ✅ Not a chain or franchise
- ✅ Not a hotel restaurant
- ✅ Not a bar/nightclub

## Results

**11 new restaurants identified** that meet criteria:

1. Maison Café (4.9)
2. Mikivi Restaurant (4.9)
3. Omu Raisu (4.9)
4. Restaurant Boreal (4.9)
5. Ravintola Lohtu (4.8)
6. Bali autotalo (4.6)
7. Restaurant Nefer Nefer Nefer (4.5)
8. Victor's Garden (4.5)
9. Esmes (4.4)
10. Rue Madame Brasserie (4.2)
11. Bouchon Carême (4.0)

## Limitations & Future Improvements

### Current Limitations:
- Depends on Google Maps data accuracy
- Some restaurants may be missed if not indexed by Google
- Review date sorting can be unreliable
- Manual verification still recommended

### Potential Improvements:
- Add Instagram scraping (#uusiravintola)
- Monitor Finnish business registry (PRH) for new restaurant registrations
- Set up automated weekly runs to catch new openings
- Add TripAdvisor as secondary data source

## Conclusion

While no perfect automated solution exists for tracking restaurant openings, the **oldest review date** from Google Maps proved to be the most reliable proxy for identifying new establishments. Combined with quality filters (rating, owner engagement, exclusion lists), this approach successfully identified 11 genuinely new restaurants that match WoM criteria.

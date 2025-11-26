#!/usr/bin/env python3
"""
Scrape Luma (lu.ma) Discover page for blockchain/crypto/web3 events daily.
- Uses Playwright (sync API)
- Saves to Excel and performs incremental update (external_id).
- Filters events by keywords in title/tags/description/JSON-LD/meta.

Usage:
    pip install playwright pandas openpyxl python-dateutil
    python -m playwright install
    python scrape_luma_web3.py

Crontab example (run daily at 02:00):
    0 2 * * * /usr/bin/python3 /path/to/scrape_luma_web3.py >> /var/log/luma_scraper.log 2>&1
"""

import time
import logging
import re
import json
import requests
from urllib.parse import urljoin, urlparse
from functools import wraps
from datetime import datetime, timezone

import pandas as pd
from dateutil import parser as dateparser
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# -------------- Enhanced Config with API Integration --------------
BASE_URL = "https://luma.com"
BASE_API_URL = "https://api2.luma.com"
DISCOVER_URL = "https://luma.com/discover"
OUTPUT_XLSX = "luma_web3_events.xlsx"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
SCROLL_TIMEOUT = 25              # seconds to attempt scrolling (optimized based on API insights)
PAGE_TIMEOUT = 25000             # ms: Playwright navigation timeout
POLITE_DELAY = (0.6, 1.1)        # sleep between page requests
MAX_EVENTS = None                # None => no limit. Set integer to limit events per run.
HEADLESS = True
PROXY = None

# API Headers for crypto category discovery
API_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Accept-Language": "en",
    "Origin": "https://luma.com",
    "Referer": "https://luma.com/",
    "X-Luma-Client-Type": "luma-web"
}

# Keywords to identify blockchain/crypto/web3 events (case-insensitive)
KEYWORDS = [
    "web3", "crypto", "cryptocurrency", "blockchain", "bitcoin", "ethereum", 
    "defi", "nft", "nft's", "layer2", "solana", "polygon", "cardano", "chainlink",
    "token", "smart contract", "dapp", "web 3", "metaverse", "dao", "gamefi",
    "yield farming", "staking", "mining", "wallet", "exchange", "trading",
    "altcoin", "hodl", "binance", "coinbase", "uniswap", "opensea",
    "avalanche", "terra", "cosmos", "polkadot", "near", "fantom",
    "decentralized", "consensus", "peer-to-peer", "p2p", "fintech blockchain",
    "digital assets", "tokenomics", "liquidity pool", "flash loan",
    "cross-chain", "interoperability", "zero knowledge", "zk", "rollup",
    "dex", "cefi", "cbdc", "stablecoin", "depin", "rwa", "tokenization"
]
KEYWORD_RE = re.compile(r"\b(" + r"|".join([re.escape(k) for k in KEYWORDS]) + r")\b", re.IGNORECASE)

# -------------- Logging --------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("luma-web3-scraper")

# -------------- Utilities --------------
def retry(max_attempts=3, delay=1.0, allowed_exceptions=(Exception,)):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exc = e
                    logger.warning("Attempt %d/%d failed for %s: %s", attempt, max_attempts, func.__name__, e)
                    time.sleep(delay * attempt)
            logger.error("All %d attempts failed for %s. Last error: %s", max_attempts, func.__name__, last_exc)
            raise last_exc
        return wrapper
    return deco

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def normalize_datetime(dt_text):
    if not dt_text:
        return None
    try:
        dt = dateparser.parse(dt_text)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return dt_text.strip()

def is_candidate_link(href: str) -> bool:
    """
    Heuristic: Luma event links are short path tokens like '/wgwqmabo' or '/abc1234'.
    Avoid links that clearly point to non-events (e.g., '/discover', '/about', absolute URLs external).
    """
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme and parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
        # external link
        return False
    path = parsed.path if parsed.path else href
    path = path.strip("/")
    # ignore empty, long paths or known non-event paths
    if not path or path.lower().startswith(("discover", "about", "pricing", "help", "terms")):
        return False
    # Luma event slugs are usually short tokens; accept tokens under 20 chars and no slashes
    if "/" in path:
        return False
    if 2 <= len(path) <= 40:
        return True
    return False

def contains_keywords(text: str) -> bool:
    if not text:
        return False
    return bool(KEYWORD_RE.search(text))

# -------------- Scraper core --------------
class LumaScraper:
    def __init__(self):
        self.out = []
        self.seen = set()
        self.stats = {"found": 0, "scraped": 0, "filtered_out": 0, "api_calls": 0}
        self.target_event_count = 879  # From API discovery
        self.crypto_calendars = []

    @retry(max_attempts=2, delay=1.0, allowed_exceptions=(PWTimeoutError, Exception))
    def load_page(self, page, url, wait_until="domcontentloaded"):
        logger.debug("Navigate to %s", url)
        page.goto(url, wait_until=wait_until, timeout=PAGE_TIMEOUT)

    def discover_crypto_calendars(self):
        """Discover crypto-focused calendars using the Luma API."""
        try:
            logger.info("🔍 Discovering crypto calendars via API...")
            response = requests.get(f"{BASE_API_URL}/discover/category/get-page?slug=crypto", 
                                  headers=API_HEADERS, timeout=10)
            response.raise_for_status()
            self.stats["api_calls"] += 1
            
            data = response.json()
            event_count = data.get("category", {}).get("event_count", 0)
            logger.info(f"📊 API reports {event_count} total crypto events available")
            self.target_event_count = event_count
            
            # Extract timeline calendars (active crypto events)
            timeline_calendars = data.get("timeline_calendars", [])
            featured_calendars = data.get("featured_calendars", [])
            
            for calendar_info in timeline_calendars + featured_calendars:
                cal_data = calendar_info.get("calendar", {})
                cal_slug = cal_data.get("slug")
                cal_name = cal_data.get("name", "Unknown")
                cal_event_count = calendar_info.get("event_count", 0)
                
                if cal_slug and cal_event_count > 0:
                    calendar_url = f"{BASE_URL}/{cal_slug}"
                    self.crypto_calendars.append({
                        "name": cal_name,
                        "slug": cal_slug,
                        "url": calendar_url,
                        "event_count": cal_event_count,
                        "type": "timeline" if calendar_info in timeline_calendars else "featured"
                    })
            
            # Sort by event count (highest first) for prioritized scraping
            self.crypto_calendars.sort(key=lambda x: x["event_count"], reverse=True)
            
            logger.info(f"🎯 Found {len(self.crypto_calendars)} crypto-focused calendars:")
            for cal in self.crypto_calendars[:5]:  # Show top 5
                logger.info(f"   • {cal['name']}: {cal['event_count']} events ({cal['type']})")
            
            return self.crypto_calendars
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to discover crypto calendars via API: {e}")
            return []

    def infinite_scroll(self, page, timeout=SCROLL_TIMEOUT, expected_events=None):
        """Enhanced scrolling with progress tracking and adaptive timeout."""
        logger.info(f"📜 Scrolling for up to {timeout}s (expecting {expected_events or 'unknown'} events)...")
        start = time.time()
        prev_height = -1
        stable_count = 0
        events_found = 0
        last_event_count = 0
        
        while time.time() - start < timeout:
            try:
                # Count current event links for progress tracking
                current_links = len(page.query_selector_all("a[href]"))
                if current_links > events_found:
                    events_found = current_links
                    if events_found - last_event_count >= 10:  # Log every 10 new events
                        logger.info(f"   📈 Found {events_found} links so far...")
                        last_event_count = events_found
                        stable_count = 0  # Reset when finding new content
                
                # Check if we've reached expected target
                if expected_events and events_found >= expected_events * 0.8:  # 80% of target
                    logger.info(f"   🎯 Reached ~80% of expected events ({events_found}/{expected_events})")
                    timeout = min(timeout, (time.time() - start) + 15)  # Give 15 more seconds
                
                height = page.evaluate("() => document.body.scrollHeight")
                
                # Enhanced scrolling techniques
                page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.6)
                
                # Scroll by chunks to trigger lazy loading
                page.evaluate("() => window.scrollBy(0, 1200)")
                time.sleep(0.4)
                
                # Look for load more buttons with enhanced selectors
                load_more_selectors = [
                    "button:has-text('Show more')", "button:has-text('Load more')", 
                    "a:has-text('Show more')", "a:has-text('Load more')",
                    "[data-testid='load-more']", ".load-more-button", 
                    "button[aria-label*='load']", "button[aria-label*='more']"
                ]
                
                for selector in load_more_selectors:
                    try:
                        load_more = page.query_selector(selector)
                        if load_more and load_more.is_visible():
                            logger.info(f"   🔄 Clicking load more: {selector}")
                            load_more.click()
                            time.sleep(2.5)
                            stable_count = 0
                            break
                    except Exception:
                        continue
                
                # Check stability
                if height == prev_height:
                    stable_count += 1
                    if stable_count < 6:  # More patience for crypto category
                        time.sleep(1.8)
                        # Try aggressive scroll to very bottom
                        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight + 2000)")
                        time.sleep(2)
                        continue
                    else:
                        logger.info(f"   ✅ Page stable after loading {events_found} links")
                        break
                else:
                    stable_count = 0
                    prev_height = height
                
            except Exception as e:
                logger.debug("Scroll evaluation failed: %s", e)
                break
                
        elapsed = time.time() - start
        final_links = len(page.query_selector_all("a[href]"))
        logger.info(f"📊 Scroll complete: {final_links} total links in {elapsed:.1f}s")
        return final_links

    def collect_event_links(self, page):
        anchors = page.query_selector_all("a[href]")
        urls = set()
        for a in anchors:
            href = a.get_attribute("href")
            if is_candidate_link(href):
                full = urljoin(BASE_URL, href)
                urls.add(full)
        logger.info("Collected %d candidate links", len(urls))
        return list(urls)

    def extract_json_ld(self, page):
        """Try to read JSON-LD script[type='application/ld+json'] and return parsed data."""
        try:
            scripts = page.query_selector_all("script[type='application/ld+json']")
            for s in scripts:
                raw = s.inner_text().strip()
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                    if isinstance(data, dict) or isinstance(data, list):
                        return data
                except Exception:
                    # sometimes JSON-LD contains multiple objects or trailing commas; try safe fix
                    try:
                        # attempt to find JSON object start
                        idx = raw.find("{")
                        j = json.loads(raw[idx:])
                        return j
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def extract_meta_content(self, page, selector_or_name):
        """Try selectors first, then meta[name=...]"""
        try:
            el = page.query_selector(selector_or_name)
            if el:
                return el.inner_text().strip()
        except Exception:
            pass
        # meta fallback
        try:
            meta = page.query_selector(f"meta[name='{selector_or_name}'], meta[property='{selector_or_name}']")
            if meta:
                return meta.get_attribute("content")
        except Exception:
            pass
        return None

    def parse_event_page(self, page, url):
        self.load_page(page, url)
        time.sleep(0.35)  # let dynamic pieces settle a moment

        # Helper to safely query text
        def text(selector):
            try:
                el = page.query_selector(selector)
                return el.inner_text().strip() if el else None
            except Exception:
                return None

        def attr(selector, name):
            try:
                el = page.query_selector(selector)
                return el.get_attribute(name) if el else None
            except Exception:
                return None

        # Try JSON-LD first (often contains structured event data)
        jsonld = self.extract_json_ld(page)
        title = None
        date_time = None
        venue = None
        description = None
        organizer = None
        ticket_url = None
        image_url = None
        category_tags = []

        if jsonld:
            # JSON-LD can be dict or list; find an object with "@type": "Event"
            j = jsonld
            if isinstance(j, list):
                items = j
            else:
                items = [j]
            for itm in items:
                try:
                    if isinstance(itm, dict) and itm.get("@type", "").lower() == "event":
                        title = itm.get("name") or title
                        # startDate/endDate
                        date_time = itm.get("startDate") or itm.get("start") or date_time
                        description = itm.get("description") or description
                        image_url = itm.get("image") or image_url
                        loc = itm.get("location")
                        if isinstance(loc, dict):
                            venue = loc.get("name") or loc.get("address") or venue
                        # offers/ticket URL
                        offers = itm.get("offers")
                        if isinstance(offers, dict):
                            ticket_url = offers.get("url") or ticket_url
                        if "performer" in itm:
                            organizer = itm.get("performer") or organizer
                        # tags
                        tags = itm.get("keywords") or itm.get("category") or itm.get("tags")
                        if tags:
                            if isinstance(tags, list):
                                category_tags.extend(tags)
                            else:
                                category_tags.append(str(tags))
                except Exception:
                    continue

        # Fallback selectors (robust multi-selector approach)
        title = title or text("h1") or text("header h1") or text("meta[property='og:title']") or text("meta[name='twitter:title']")
        description = description or text("div.event-description") or text("div.description") or text("section .description") or attr("meta[name='description']", "content")
        image_url = image_url or attr("img.cover, img.event-cover, .event-image img", "src") or attr("meta[property='og:image']", "content")
        date_text = date_time or text("time") or text("div .event-date") or text(".event-meta time")
        venue = venue or text(".venue") or text(".location") or text("address") or text(".event-location")
        organizer = organizer or text(".organizer") or text("a.host") or text(".event-host") or text(".presented-by")
        # ticket link heuristics
        try:
            t_el = page.query_selector("a[href*='checkout'], a[href*='ticket'], button:has-text('Register'), a:has-text('Register'), a:has-text('Tickets')")
            if t_el:
                ticket_href = t_el.get_attribute("href")
                ticket_url = urljoin(BASE_URL, ticket_href) if ticket_href else ticket_url
        except Exception:
            pass

        # collect tags (visible tag elements)
        try:
            tag_els = page.query_selector_all("a.tag, a.category, .tags a, .event-tags a")
            for te in tag_els:
                try:
                    txt = te.inner_text().strip()
                    if txt:
                        category_tags.append(txt)
                except Exception:
                    continue
        except Exception:
            pass

        # final normalizations
        date_time_norm = normalize_datetime(date_text) if date_text else None
        # Handle case where image_url might be a list
        if isinstance(image_url, list):
            image_url = image_url[0] if image_url else None
        # Ensure image_url is a string and handle relative URLs
        if image_url and isinstance(image_url, str) and not image_url.startswith("http"):
            image_url = urljoin(BASE_URL, image_url)
        elif not isinstance(image_url, str):
            image_url = None

        # If nothing found in title or description, try meta tags as last resort
        if not title:
            title = page.title() or None

        parsed = {
            "external_id": url,
            "title": title,
            "date_time": date_time_norm,
            "raw_date_text": date_text,
            "venue": venue,
            "organizer": organizer,
            "description": description,
            "category_tags": ", ".join(dict.fromkeys([t.strip() for t in category_tags if t])),
            "ticket_url": ticket_url,
            "image_url": image_url,
            "scraped_at": now_iso(),
            "source": BASE_URL,
        }
        return parsed

    def matches_web3(self, record: dict) -> bool:
        """Return True if any field contains web3/crypto keywords or if it came from crypto category."""
        # If the external_id (URL) indicates it came from the crypto category, accept it
        url = record.get("external_id", "")
        
        # Check title, description, tags, raw_date_text, category_tags
        fields = [
            record.get("title") or "",
            record.get("description") or "",
            record.get("category_tags") or "",
            record.get("raw_date_text") or "",
            record.get("venue") or "",
            record.get("organizer") or "",
        ]
        
        # join and check regex
        hay = " ".join(fields)
        if contains_keywords(hay):
            return True
            
        # For events with very minimal data, be more lenient if they have crypto-related terms
        # even if they don't match the full keyword list
        basic_crypto_terms = ["crypto", "bitcoin", "blockchain", "ethereum", "web3", "defi", "nft"]
        for term in basic_crypto_terms:
            if term.lower() in hay.lower():
                return True
                
        return False

    def load_existing(self):
        """Load existing output file (if exists) to support incremental updates."""
        try:
            df = pd.read_excel(OUTPUT_XLSX, engine="openpyxl")
            existing = {row["external_id"]: row for _, row in df.iterrows()}
            logger.info("Loaded %d existing records from %s", len(existing), OUTPUT_XLSX)
            return existing
        except FileNotFoundError:
            logger.info("No existing file; starting fresh.")
            return {}
        except Exception as e:
            logger.warning("Failed to load existing file: %s. Starting fresh.", e)
            return {}

    def run(self):
        existing = self.load_existing()
        updated = dict(existing)  # will store updated rows keyed by external_id
        all_links = set()

        # 🚀 Step 1: Discover crypto calendars via API
        self.discover_crypto_calendars()

        with sync_playwright() as p:
            chromium = p.chromium
            launch_args = {"headless": HEADLESS}
            if PROXY:
                launch_args["proxy"] = {"server": PROXY}
            browser = chromium.launch(**launch_args)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            try:
                # 🎯 Step 2: Build enhanced URL list with API insights
                discover_urls = [
                    f"{BASE_URL}/discover?category=crypto",  # Primary crypto category
                    DISCOVER_URL,  # Main discover page
                    f"{BASE_URL}/discover?category=technology",
                    f"{BASE_URL}/discover?category=business", 
                    f"{BASE_URL}/discover?category=finance",
                ]
                
                # Add crypto calendar URLs from API discovery
                logger.info(f"🎯 Adding {len(self.crypto_calendars)} crypto-focused calendar URLs...")
                for cal in self.crypto_calendars:
                    if cal["event_count"] > 0:  # Only add calendars with events
                        discover_urls.append(cal["url"])
                        logger.info(f"   + {cal['name']}: {cal['event_count']} events")
                
                # Add targeted search queries
                search_terms = ["blockchain", "crypto", "web3", "bitcoin", "ethereum", "defi", "nft", "dao", "token", "cryptocurrency", "hackathon", "solana"]
                for term in search_terms:
                    discover_urls.append(f"{BASE_URL}/discover?q={term}")
                
                logger.info(f"📋 Total URLs to process: {len(discover_urls)}")
                
                # 🔄 Step 3: Process all URLs with adaptive timeouts
                for idx, url in enumerate(discover_urls, 1):
                    try:
                        logger.info(f"\n[{idx}/{len(discover_urls)}] 🌐 Processing: {url}")
                        self.load_page(page, url)
                        
                        # Determine optimal scroll timeout based on content type
                        expected_events = None
                        if "category=crypto" in url:
                            scroll_timeout = 120  # Extended for main crypto category
                            expected_events = self.target_event_count
                            logger.info(f"   🎯 Crypto category: targeting {expected_events} events")
                        elif any(cal["url"] == url for cal in self.crypto_calendars):
                            # Calendar-specific optimization
                            cal_info = next(cal for cal in self.crypto_calendars if cal["url"] == url)
                            scroll_timeout = min(60, max(20, cal_info["event_count"] * 2))
                            expected_events = cal_info["event_count"]
                            logger.info(f"   📅 Calendar '{cal_info['name']}': expecting {expected_events} events")
                        else:
                            scroll_timeout = SCROLL_TIMEOUT
                        
                        # Enhanced scrolling with progress tracking
                        self.infinite_scroll(page, timeout=scroll_timeout, expected_events=expected_events)
                        
                        # Collect and track progress
                        page_links = self.collect_event_links(page)
                        new_links = len(page_links)
                        all_links.update(page_links)
                        
                        # Progress reporting
                        total_unique = len(all_links)
                        progress_pct = (total_unique / self.target_event_count * 100) if self.target_event_count else 0
                        logger.info(f"   📊 Page: +{new_links} links | Total: {total_unique} unique | Progress: {progress_pct:.1f}%")
                        
                        # Brief delay between pages
                        time.sleep(2.2)
                        
                    except Exception as e:
                        logger.error("❌ Failed to process %s: %s", url, e)
                        continue
                
                # 📊 Step 4: Process discovered events
                links = sorted(list(all_links))
                if MAX_EVENTS:
                    links = links[:MAX_EVENTS]
                    logger.info(f"⚠️  Limiting to {MAX_EVENTS} events (from {len(all_links)} discovered)")
                
                logger.info(f"\n🎯 DISCOVERY COMPLETE: {len(links)} unique candidate links found")
                logger.info(f"📊 Target coverage: {len(links)}/{self.target_event_count} events ({len(links)/self.target_event_count*100:.1f}%)")
                self.stats["found"] = len(links)

                # Process individual events with enhanced progress tracking
                for idx, link in enumerate(links, start=1):
                    if link in self.seen or link in updated:
                        continue
                    self.seen.add(link)
                    
                    try:
                        # Progress reporting every 25 events
                        if idx % 25 == 0:
                            logger.info(f"\n📈 PROGRESS [{idx}/{len(links)}]: {self.stats['scraped']} scraped, {self.stats['filtered_out']} filtered")
                        
                        logger.debug(f"[{idx}/{len(links)}] 🔍 Scraping: {link}")
                        rec = self.parse_event_page(page, link)
                        
                        # Enhanced keyword filtering
                        if not self.matches_web3(rec):
                            logger.debug(f"❌ Filtered OUT: {rec.get('title', 'No title')}")
                            self.stats["filtered_out"] += 1
                            time.sleep((POLITE_DELAY[0] + POLITE_DELAY[1]) / 2)
                            continue
                        
                        # Success! Save the event
                        updated[rec["external_id"]] = rec
                        self.out.append(rec)
                        self.stats["scraped"] += 1
                        logger.debug(f"✅ Scraped: {rec.get('title', 'No title')}")
                        
                        # Adaptive delay based on success rate
                        time.sleep(POLITE_DELAY[0] + (POLITE_DELAY[1] - POLITE_DELAY[0]) * 0.5)
                        
                    except Exception as e:
                        logger.error("💥 Error scraping %s: %s", link, e)
                        continue
            finally:
                try:
                    context.close()
                    browser.close()
                except Exception:
                    pass

        # 💾 Step 5: Save results with enhanced reporting
        if updated:
            df = pd.DataFrame.from_dict(updated, orient="index")
            # Reorder columns for readability
            cols = ["external_id", "title", "date_time", "raw_date_text", "venue", "organizer",
                    "category_tags", "description", "ticket_url", "image_url", "scraped_at", "source"]
            cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
            df = df[cols]
            
            # Save to Excel
            df.to_excel(OUTPUT_XLSX, index=False, engine="openpyxl")
            
            # Enhanced completion report
            total_events = len(df)
            new_events = self.stats["scraped"]
            existing_events = total_events - new_events
            
            logger.info(f"\n🎉 SCRAPING COMPLETE!")
            logger.info(f"📊 Final Results:")
            logger.info(f"   • Total events in database: {total_events}")
            logger.info(f"   • New events scraped: {new_events}")
            logger.info(f"   • Previously existing: {existing_events}")
            logger.info(f"   • API calls made: {self.stats['api_calls']}")
            logger.info(f"   • Coverage achieved: {total_events}/{self.target_event_count} ({total_events/self.target_event_count*100:.1f}%)")
            logger.info(f"💾 Saved to: {OUTPUT_XLSX}")
            
            # Quality metrics
            if self.stats["found"] > 0:
                success_rate = (self.stats["scraped"] / self.stats["found"]) * 100
                logger.info(f"📈 Success rate: {success_rate:.1f}% ({self.stats['scraped']}/{self.stats['found']} events passed filtering)")
        else:
            logger.info("⚠️  No updates to save.")

        self.stats["total_events"] = len(updated) if updated else 0
        logger.info(f"\n📋 Final Stats: {self.stats}")
        return self.stats

# -------------- Entrypoint --------------
def main():
    logger.info("🚀 Enhanced Luma Web3 Scraper started at %s", now_iso())
    logger.info("🎯 Target: Discover and scrape crypto/web3 events using API-enhanced approach")
    
    scraper = LumaScraper()
    try:
        stats = scraper.run()
        
        # Final summary
        logger.info(f"\n✅ SCRAPER COMPLETED SUCCESSFULLY!")
        logger.info(f"🎉 Found {stats.get('total_events', 0)} total crypto/web3 events")
        logger.info(f"📝 Check {OUTPUT_XLSX} for results")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Scraper interrupted by user")
    except Exception as e:
        logger.exception("💥 Scraper failed: %s", e)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🚀 AUTOMATED HYBRID LUMA CRYPTO EVENTS SCRAPER
Combines API discovery + Web scraping with daily automation at 2:00 AM
Prevents duplicates and maintains comprehensive event database
"""

import os
import requests
import time
import logging
import re
import json
from urllib.parse import urljoin, urlparse
from functools import wraps
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# Try to import Playwright (for web scraping component)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available - API-only mode")

# ============= CONFIGURATION =============
BASE_URL = "https://lu.ma"
BASE_API_URL = "https://api2.luma.com"
OUTPUT_XLSX = "luma_crypto_events_master.xlsx"
LOG_FILE = "scraper.log"

# Rate limiting
API_RATE_DELAY = 0.3
WEB_RATE_DELAY = (0.6, 1.1)

# Your authenticated session cookies (paste your latest ones here)
AUTHENTICATED_COOKIES = {
    'luma.auth-session-key': 'usr-IDN7SkDVoz3bqXE.54rbgyhfjdc0ek32cxm4',
    'luma.did': '6sh8eydys1rs062ygbv0n7ryjw5d02',
    '__cf_bm': 'GnuwvxE51PGZLgx8pFBG_y_jzEuSGtFupxPulcgytJc-1764147915-1.0.1.1-39cUvUa95E4bCiPiF.MQVepUOlaL07p4hefjYM70yOeDqvL5zmCS0R7YlcbKAfr8nyHgvnzWSblpbJbnq8kQ0mbsSNUrcDdeAftB9VD7QmU',
    'luma.first-page': '%2Fgoogle%3Fstate%3Dkoz7vddnefy8s7wwvlp88e142a4qwfyh%26code%3D4%252F0Ab32j905z3CrZyQn4GrpP73_XQwOnLaWYFgAPBlUhG0Yst8e_TKFWr6zHX9HPFAvYAc9WA%26scope%3Demail%2Bprofile%2Bhttps%253A%252F%252Fwww.googleapis.com%252Fauth%252Fuserinfo.profile%2Bhttps%253A%252F%252Fwww.googleapis.com%252Fauth%252Fuserinfo.email%2Bopenid%26authuser%3D0%26prompt%3Dconsent',
    'luma.native-referrer': 'https%3A%2F%2Fluma.com%2Fcrypto'
}

# API Headers
API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://lu.ma",
    "Referer": "https://lu.ma/crypto",
    "X-Luma-Client-Type": "luma-web",
    "X-Luma-Client-Version": "d12c8aa69edc8a6541453a87c3e5bb74c2d7ba92"
}

# Global crypto locations for comprehensive coverage
CRYPTO_LOCATIONS = [
    {"name": "San Francisco, USA", "lat": 37.7749, "lng": -122.4194},
    {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
    {"name": "London, UK", "lat": 51.5074, "lng": -0.1278},
    {"name": "Berlin, Germany", "lat": 52.5200, "lng": 13.4050},
    {"name": "Singapore", "lat": 1.3521, "lng": 103.8198},
    {"name": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503},
    {"name": "Seoul, South Korea", "lat": 37.5665, "lng": 126.9780},
    {"name": "Dubai, UAE", "lat": 25.2048, "lng": 55.2708},
    {"name": "Toronto, Canada", "lat": 43.6532, "lng": -79.3832},
    {"name": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
    {"name": "Hong Kong", "lat": 22.3193, "lng": 114.1694},
    {"name": "Delhi, India", "lat": 28.6139, "lng": 77.2090},
    {"name": "Mumbai, India", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bangalore, India", "lat": 12.9716, "lng": 77.5946},
    {"name": "Miami, USA", "lat": 25.7617, "lng": -80.1918},
    {"name": "Los Angeles, USA", "lat": 34.0522, "lng": -118.2437},
    {"name": "Amsterdam, Netherlands", "lat": 52.3676, "lng": 4.9041},
    {"name": "Zurich, Switzerland", "lat": 47.3769, "lng": 8.5417},
    {"name": "Tel Aviv, Israel", "lat": 32.0853, "lng": 34.7818},
    {"name": "Austin, USA", "lat": 30.2672, "lng": -97.7431},
    # Additional cities discovered during testing
    {"name": "Istanbul, Turkey", "lat": 41.0082, "lng": 28.9784},
    {"name": "Paris, France", "lat": 48.8566, "lng": 2.3522},
    {"name": "Madrid, Spain", "lat": 40.4168, "lng": -3.7038},
    {"name": "Rome, Italy", "lat": 41.9028, "lng": 12.4964},
    {"name": "Prague, Czech Republic", "lat": 50.0755, "lng": 14.4378},
    {"name": "Budapest, Hungary", "lat": 47.4979, "lng": 19.0402},
    {"name": "Bucharest, Romania", "lat": 44.4268, "lng": 26.1025},
    {"name": "Brussels, Belgium", "lat": 50.8503, "lng": 4.3517},
    {"name": "Cape Town, South Africa", "lat": -33.9249, "lng": 18.4241},
    {"name": "Nairobi, Kenya", "lat": -1.2921, "lng": 36.8219},
    {"name": "Lagos, Nigeria", "lat": 6.5244, "lng": 3.3792},
    {"name": "Abu Dhabi, UAE", "lat": 24.4539, "lng": 54.3773},
    {"name": "Taipei, Taiwan", "lat": 25.0330, "lng": 121.5654},
    {"name": "Manila, Philippines", "lat": 14.5995, "lng": 120.9842},
    {"name": "Kuala Lumpur, Malaysia", "lat": 3.1390, "lng": 101.6869},
    {"name": "Mexico City, Mexico", "lat": 19.4326, "lng": -99.1332},
    {"name": "São Paulo, Brazil", "lat": -23.5558, "lng": -46.6396},
    {"name": "Buenos Aires, Argentina", "lat": -34.6118, "lng": -58.3960},
    {"name": "Bogotá, Colombia", "lat": 4.7110, "lng": -74.0721},
    {"name": "Lima, Peru", "lat": -12.0464, "lng": -77.0428},
    {"name": "Beijing, China", "lat": 39.9042, "lng": 116.4074},
]

# Web scraping crypto keywords
CRYPTO_KEYWORDS = [
    "web3", "crypto", "cryptocurrency", "blockchain", "bitcoin", "ethereum", 
    "defi", "nft", "layer2", "solana", "polygon", "cardano", "chainlink",
    "token", "smart contract", "dapp", "metaverse", "dao", "gamefi",
    "yield farming", "staking", "mining", "wallet", "exchange", "trading",
    "altcoin", "hodl", "binance", "coinbase", "uniswap", "opensea",
    "avalanche", "terra", "cosmos", "polkadot", "near", "fantom",
    "decentralized", "consensus", "peer-to-peer", "p2p", "fintech blockchain",
    "digital assets", "tokenomics", "liquidity pool", "flash loan",
    "cross-chain", "interoperability", "zero knowledge", "zk", "rollup",
    "dex", "cefi", "cbdc", "stablecoin", "depin", "rwa", "tokenization",
    "hackathon", "zk-rollup", "layer-2", "web3 conference", "crypto meetup"
]

KEYWORD_RE = re.compile(r"\b(" + r"|".join([re.escape(k) for k in CRYPTO_KEYWORDS]) + r")\b", re.IGNORECASE)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("automated-hybrid-scraper")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def normalize_datetime(dt_text):
    if not dt_text:
        return None
    try:
        dt = dateparser.parse(dt_text)
        if dt and not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat() if dt else dt_text.strip()
    except Exception:
        return dt_text.strip() if dt_text else None

class AutomatedHybridScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)
        self.session.cookies.update(AUTHENTICATED_COOKIES)
        
        self.events = []
        self.stats = {
            "api_calls": 0,
            "api_events_found": 0,
            "web_events_found": 0,
            "total_new_events": 0,
            "duplicates_prevented": 0,
            "locations_processed": 0
        }
        self.existing_ids: Set[str] = set()
        self.detail_cache: Dict[str, Optional[Dict]] = {}

    def load_existing_events(self) -> pd.DataFrame:
        """Load existing events and return DataFrame + set of IDs."""
        try:
            df = pd.read_excel(OUTPUT_XLSX)
            self.existing_ids = set(df["external_id"].dropna().astype(str))
            logger.info(f"📚 Loaded {len(df)} existing events")
            return df
        except FileNotFoundError:
            logger.info("📝 No existing file found - starting fresh database")
            return pd.DataFrame()
        except Exception as e:
            logger.warning(f"⚠️  Error loading existing file: {e}")
            return pd.DataFrame()

    def api_discover_events(self) -> List[Dict]:
        """Discover events using the Luma API across all global locations."""
        logger.info("🚀 Starting API discovery phase...")
        api_events = []
        
        for idx, location in enumerate(CRYPTO_LOCATIONS, 1):
            try:
                logger.info(f"[{idx}/{len(CRYPTO_LOCATIONS)}] 🌍 {location['name']}")
                
                response = self.session.get(
                    f"{BASE_API_URL}/discover/get-paginated-events",
                    params={
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "pagination_limit": 100,
                        "slug": "crypto"
                    }
                )
                response.raise_for_status()
                self.stats["api_calls"] += 1
                
                data = response.json()
                entries = data.get("entries", [])
                logger.info(f"   📊 Found {len(entries)} events")
                
                for entry in entries:
                    parsed_event = self.parse_api_event(entry, location["name"])
                    if parsed_event and parsed_event["external_id"] not in self.existing_ids:
                        api_events.append(parsed_event)
                        self.existing_ids.add(parsed_event["external_id"])  # Prevent duplicates within run
                        self.stats["api_events_found"] += 1
                    elif parsed_event:
                        self.stats["duplicates_prevented"] += 1
                
                self.stats["locations_processed"] += 1
                time.sleep(API_RATE_DELAY)
                
            except Exception as e:
                logger.error(f"❌ Failed to process {location['name']}: {e}")
                continue
        
        logger.info(f"🎯 API Discovery: {len(api_events)} new events found")
        return api_events

    def parse_api_event(self, entry: Dict, location_name: str) -> Optional[Dict]:
        """Parse event from API response."""
        try:
            event_data = entry.get("event", {})
            
            # Debug: Print the structure we're getting
            logger.debug(f"Processing event: {event_data.get('name', 'No name')}")
            logger.debug(f"geo_address_info available: {'geo_address_info' in event_data}")
            logger.debug(f"hosts available: {len(entry.get('hosts', []))}")
            event_id = entry.get("api_id")
            
            if not event_id:
                return None
            
            # Build full event URL
            slug = (event_data.get("url") or "").strip("/")
            event_url = self.build_event_url(slug, event_id)
            
            # Extract venue information from correct API field
            geo_data = event_data.get("geo_address_info", {})
            venue_parts = []
            
            # Use the available geo_address_info structure
            if geo_data.get("address"):
                venue_parts.append(str(geo_data["address"]))
            if geo_data.get("city_state"):
                venue_parts.append(str(geo_data["city_state"]))
            elif geo_data.get("region"):
                venue_parts.append(str(geo_data["region"]))
            if geo_data.get("country"):
                venue_parts.append(str(geo_data["country"]))
                
            venue = ", ".join(venue_parts) if venue_parts else None
            
            # Extract organizer from hosts array (corrected structure)
            hosts = entry.get("hosts", [])
            organizer_names = []
            for host in hosts:
                # Hosts are directly in the array, not nested under 'user'
                if host.get("name"):
                    organizer_names.append(host["name"])
            organizer = ", ".join(organizer_names) if organizer_names else None
            
            # Extract image
            cover_image = entry.get("cover_image", {})
            image_url = None
            if cover_image:
                image_url = cover_image.get("url") or cover_image.get("image_url")

            # Enrich with HTML page to capture description & accurate timeline/links
            detail_data = self.fetch_event_detail_from_web(slug) if slug else None
            description = event_data.get("description")
            start_iso = normalize_datetime(entry.get("start_at"))
            end_iso = normalize_datetime(entry.get("end_at"))
            raw_date_text = None
            if detail_data:
                description = detail_data.get("description") or description
                if detail_data.get("startDate"):
                    raw_date_text = detail_data.get("startDate")
                    start_iso = normalize_datetime(detail_data["startDate"])
                if detail_data.get("endDate"):
                    end_iso = normalize_datetime(detail_data["endDate"])
                venue = venue or detail_data.get("venue")
                image_url = image_url or detail_data.get("image")
                if detail_data.get("ticket_url"):
                    event_url = detail_data["ticket_url"]
                extra_tags = detail_data.get("keywords")
            else:
                extra_tags = []
            
            return {
                "external_id": event_id,
                "event_slug": slug or None,
                "title": event_data.get("name"),
                "date_time": start_iso,
                "end_time": end_iso,
                "raw_date_text": raw_date_text,
                "venue": venue,
                "organizer": organizer,
                "description": description,
                "category_tags": self.build_category_tags(extra_tags),
                "ticket_url": event_url,
                "image_url": image_url,
                "guest_count": entry.get("guest_count", 0),
                "ticket_count": entry.get("ticket_count", 0),
                "discovery_location": location_name,
                "timezone": event_data.get("timezone"),
                "scraped_at": now_iso(),
                "source": "api-automated",
                "waitlist_active": entry.get("waitlist_active", False),
                "raw_api_data": json.dumps(entry)
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse API event {entry.get('api_id', 'unknown')}: {e}")
            return None

    def web_scrape_events(self) -> List[Dict]:
        """Web scrape additional events (optional enhanced coverage)."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.info("⚠️  Playwright not available - skipping web scraping")
            return []
        
        logger.info("🌐 Starting web scraping phase...")
        web_events = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Focus on crypto category for targeted web scraping
                crypto_urls = [
                    f"{BASE_URL}/discover?category=crypto",
                    f"{BASE_URL}/discover?q=blockchain",
                    f"{BASE_URL}/discover?q=web3",
                ]
                
                for url in crypto_urls:
                    try:
                        logger.info(f"🔍 Scraping: {url}")
                        page.goto(url, timeout=30000)
                        time.sleep(2)
                        
                        # Enhanced scroll to load more events
                        self.enhanced_scroll(page, timeout=20)
                        
                        # Collect event links
                        event_links = self.collect_event_links(page)
                        logger.info(f"   📋 Found {len(event_links)} potential events")
                        
                        # Sample and parse a few events (to avoid long processing)
                        for link in event_links[:10]:  # Limit for automation
                            if any(link.endswith(existing_id) for existing_id in self.existing_ids):
                                continue
                                
                            try:
                                parsed_event = self.parse_web_event(page, link)
                                if parsed_event and self.contains_crypto_keywords(parsed_event):
                                    if parsed_event["external_id"] not in self.existing_ids:
                                        web_events.append(parsed_event)
                                        self.existing_ids.add(parsed_event["external_id"])
                                        self.stats["web_events_found"] += 1
                                    else:
                                        self.stats["duplicates_prevented"] += 1
                                        
                                time.sleep(WEB_RATE_DELAY[0])
                                
                            except Exception as e:
                                logger.debug(f"Failed to parse {link}: {e}")
                                continue
                                
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Failed to scrape {url}: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
        
        logger.info(f"🎯 Web Scraping: {len(web_events)} new events found")
        return web_events

    @staticmethod
    def build_event_url(slug: Optional[str], event_id: str) -> str:
        if slug:
            slug = slug.strip("/")
            return f"{BASE_URL}/{slug}"
        return f"{BASE_URL}/{event_id}"

    @staticmethod
    def build_category_tags(extra_tags: Optional[List[str]]) -> str:
        tags = ["crypto", "web3", "api-sourced"]
        if extra_tags:
            tags.extend(extra_tags)
        # Remove blanks and preserve order
        seen = []
        for tag in tags:
            if tag and tag not in seen:
                seen.append(tag)
        return ",".join(seen)

    def fetch_event_detail_from_web(self, slug: str) -> Optional[Dict]:
        """Fetch event page HTML and extract description & schedule via JSON-LD."""
        if not slug:
            return None
        slug = slug.strip("/")
        if slug in self.detail_cache:
            return self.detail_cache[slug]

        event_url = f"{BASE_URL}/{slug}"
        headers = {
            "User-Agent": API_HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Referer": f"{BASE_URL}/discover?category=crypto",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            response = requests.get(
                event_url,
                headers=headers,
                cookies=self.session.cookies,
                timeout=20,
            )
            response.raise_for_status()
        except Exception as e:
            logger.debug(f"Failed to fetch event page for {slug}: {e}")
            self.detail_cache[slug] = None
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        ld_event = self.extract_event_jsonld(soup)
        if not ld_event:
            self.detail_cache[slug] = None
            return None

        description = self.clean_description(ld_event.get("description"))
        location = ld_event.get("location", {})
        venue = None
        if isinstance(location, dict):
            venue = location.get("name") or location.get("address")

        keywords = []
        raw_keywords = ld_event.get("keywords") or ld_event.get("category")
        if raw_keywords:
            if isinstance(raw_keywords, list):
                keywords = [str(k).strip() for k in raw_keywords if k]
            else:
                keywords = [str(raw_keywords).strip()]

        detail = {
            "description": description,
            "startDate": ld_event.get("startDate"),
            "endDate": ld_event.get("endDate"),
            "image": ld_event.get("image"),
            "venue": venue,
            "keywords": keywords,
            "ticket_url": ld_event.get("url") if ld_event.get("url", "").startswith("http") else event_url,
        }
        self.detail_cache[slug] = detail
        return detail

    @staticmethod
    def extract_event_jsonld(soup: BeautifulSoup) -> Optional[Dict]:
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        for script in scripts:
            raw = script.string or script.get_text()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except Exception:
                continue
            nodes = data if isinstance(data, list) else [data]
            for node in nodes:
                node_type = node.get("@type")
                if isinstance(node_type, list):
                    is_event = any(t.lower() == "event" for t in node_type if isinstance(t, str))
                else:
                    is_event = isinstance(node_type, str) and node_type.lower() == "event"
                if is_event:
                    return node
        return None

    @staticmethod
    def clean_description(desc: Optional[str]) -> Optional[str]:
        if not desc:
            return None
        try:
            text = BeautifulSoup(desc, "html.parser").get_text("\n")
            return text.strip()
        except Exception:
            return desc.strip()

    def enhanced_scroll(self, page, timeout=20):
        """Enhanced scrolling for web scraping."""
        start = time.time()
        prev_height = -1
        stable_count = 0
        
        while time.time() - start < timeout:
            try:
                height = page.evaluate("() => document.body.scrollHeight")
                page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.8)
                
                # Check for load more buttons
                try:
                    load_more = page.query_selector("button:has-text('Show more'), button:has-text('Load more')")
                    if load_more and load_more.is_visible():
                        load_more.click()
                        time.sleep(2)
                        stable_count = 0
                        continue
                except:
                    pass
                
                if height == prev_height:
                    stable_count += 1
                    if stable_count >= 4:
                        break
                else:
                    stable_count = 0
                    prev_height = height
                    
            except Exception:
                break

    def collect_event_links(self, page) -> List[str]:
        """Collect event links from page."""
        links = set()
        try:
            anchors = page.query_selector_all("a[href]")
            for anchor in anchors:
                href = anchor.get_attribute("href")
                if self.is_event_link(href):
                    full_url = urljoin(BASE_URL, href)
                    links.add(full_url)
        except Exception as e:
            logger.debug(f"Error collecting links: {e}")
        
        return list(links)

    def is_event_link(self, href: str) -> bool:
        """Check if link is a valid event link (not category pages)."""
        if not href:
            return False
        
        parsed = urlparse(href)
        if parsed.scheme and parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
            return False
            
        path = parsed.path.strip("/") if parsed.path else href.strip("/")
        
        # Exclude system pages and category pages
        excluded_starts = ("discover", "about", "pricing", "help", "terms", "login", "signup", 
                          "calendar", "user", "profile", "settings", "notifications")
        if not path or path.lower().startswith(excluded_starts):
            return False
            
        # Exclude category/location pages (these usually are just location names)
        location_words = ["san-francisco", "new-york", "london", "berlin", "singapore", "tokyo", 
                         "seoul", "dubai", "toronto", "sydney", "hong-kong", "mumbai", "bangalore",
                         "miami", "los-angeles", "amsterdam", "zurich", "tel-aviv", "austin",
                         "istanbul", "paris", "madrid", "rome", "prague", "budapest", "bucharest",
                         "brussels", "cape-town", "nairobi", "lagos", "abu-dhabi", "taipei",
                         "manila", "kuala-lumpur", "mexico-city", "sao-paulo", "buenos-aires",
                         "bogota", "lima", "beijing"]
        
        if path.lower() in location_words:
            return False
            
        # Valid Luma event patterns (must be event IDs, not words)
        if "/" in path:
            parts = path.split("/")
            if len(parts) == 2:
                # Second part should look like an event ID (alphanumeric, not just words)
                event_id = parts[1]
                if len(event_id) >= 8 and any(c.isdigit() or c in 'abcdef' for c in event_id.lower()):
                    return True
        elif len(path) >= 8 and any(c.isdigit() or c in 'abcdef' for c in path.lower()):
            # Direct event ID pattern
            return True
            
        return False

    def parse_web_event(self, page, url: str) -> Optional[Dict]:
        """Parse individual web event."""
        try:
            page.goto(url, timeout=30000)
            time.sleep(1)
            
            def text(selector):
                try:
                    el = page.query_selector(selector)
                    return el.inner_text().strip() if el else None
                except:
                    return None
            
            def attr(selector, name):
                try:
                    el = page.query_selector(selector)
                    return el.get_attribute(name) if el else None
                except:
                    return None
            
            title = text("h1") or text("header h1") or page.title()
            description = (text("div.event-description") or 
                         text("div.description") or 
                         attr("meta[name='description']", "content"))
            
            date_text = text("time") or text("div .event-date")
            venue = text(".venue") or text(".location") or text("address")
            organizer = text(".organizer") or text("a.host")
            
            image_url = (attr("img.cover, img.event-cover, .event-image img", "src") or 
                        attr("meta[property='og:image']", "content"))
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(BASE_URL, image_url)
            
            # Extract event ID from URL
            event_id = url.split("/")[-1] if "/" in url else url
            
            return {
                "external_id": event_id,
                "title": title,
                "date_time": normalize_datetime(date_text),
                "raw_date_text": date_text,
                "venue": venue,
                "organizer": organizer,
                "description": description,
                "category_tags": "crypto,web3,web-scraped",
                "ticket_url": url,
                "image_url": image_url,
                "scraped_at": now_iso(),
                "source": "web-automated",
                "guest_count": None,
                "ticket_count": None,
                "discovery_location": "web-scraping",
                "waitlist_active": None,
                "raw_api_data": None
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse web event {url}: {e}")
            return None

    def contains_crypto_keywords(self, event: Dict) -> bool:
        """Check if event contains crypto/web3 keywords."""
        fields = [
            event.get("title") or "",
            event.get("description") or "",
            event.get("category_tags") or "",
            event.get("venue") or "",
            event.get("organizer") or ""
        ]
        
        text = " ".join(fields).lower()
        return bool(KEYWORD_RE.search(text))

    def save_events(self, new_events: List[Dict]) -> None:
        """Save new events to Excel, preventing duplicates."""
        if not new_events:
            logger.info("ℹ️  No new events to save")
            return
        
        # Load existing data
        try:
            existing_df = pd.read_excel(OUTPUT_XLSX)
        except FileNotFoundError:
            existing_df = pd.DataFrame()
        
        # Create new events DataFrame
        new_df = pd.DataFrame(new_events)
        
        # Combine and deduplicate
        if not existing_df.empty:
            # Ensure column compatibility
            all_columns = set(existing_df.columns) | set(new_df.columns)
            for col in all_columns:
                if col not in existing_df.columns:
                    existing_df[col] = None
                if col not in new_df.columns:
                    new_df[col] = None
            
            # Combine DataFrames
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Remove duplicates based on external_id
            combined_df = combined_df.drop_duplicates(subset=["external_id"], keep="last")
        else:
            combined_df = new_df
        
        # Sort by scraped_at (newest first)
        if "scraped_at" in combined_df.columns:
            combined_df = combined_df.sort_values("scraped_at", ascending=False)
        
        # Save to Excel with graceful fallback if the file is open elsewhere
        try:
            combined_df.to_excel(OUTPUT_XLSX, index=False)
        except PermissionError:
            pending_path = OUTPUT_XLSX + ".pending"
            combined_df.to_excel(pending_path, index=False)
            logger.error(
                "❌ Unable to overwrite %s (file is open?). "
                "Saved fresh data to %s instead. Close the Excel file and "
                "replace it manually, or rerun the scraper once it's closed.",
                OUTPUT_XLSX,
                pending_path,
            )
            raise
        
        total_events = len(combined_df)
        new_events_count = len(new_events)
        self.stats["total_new_events"] = new_events_count
        
        logger.info(f"💾 Saved {new_events_count} new events")
        logger.info(f"📊 Database now contains {total_events} total events")

    def run(self) -> Dict:
        """Main execution method."""
        start_time = datetime.now()
        logger.info(f"🚀 Starting Automated Hybrid Scraper at {start_time}")
        
        # Load existing events
        existing_df = self.load_existing_events()
        
        # Phase 1: API Discovery
        api_events = self.api_discover_events()
        
        # Phase 2: Web Scraping (optional, lightweight)
        web_events = self.web_scrape_events()
        
        # Combine all new events
        all_new_events = api_events + web_events
        
        # Save to Excel with deduplication
        self.save_events(all_new_events)
        
        # Final reporting
        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds()
        
        self.stats["runtime_seconds"] = runtime
        self.stats["start_time"] = start_time.isoformat()
        self.stats["end_time"] = end_time.isoformat()
        
        logger.info(f"🎉 AUTOMATED SCRAPING COMPLETE!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   • Runtime: {runtime:.1f} seconds")
        logger.info(f"   • API calls: {self.stats['api_calls']}")
        logger.info(f"   • Locations processed: {self.stats['locations_processed']}")
        logger.info(f"   • New API events: {self.stats['api_events_found']}")
        logger.info(f"   • New web events: {self.stats['web_events_found']}")
        logger.info(f"   • Total new events: {self.stats['total_new_events']}")
        logger.info(f"   • Duplicates prevented: {self.stats['duplicates_prevented']}")
        logger.info(f"💾 Results in: {OUTPUT_XLSX}")
        
        return self.stats

def main():
    """Main entry point for automated execution."""
    try:
        scraper = AutomatedHybridScraper()
        stats = scraper.run()
        return stats
    except Exception as e:
        logger.exception(f"💥 Scraper failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    main()
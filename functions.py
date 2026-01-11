from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

# Reusable session for connection pooling
_session = None

def get_session():
    """Get or create a reusable requests session with connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=1
        )
        _session.mount('http://', adapter)
        _session.mount('https://', adapter)
    return _session

def normalize_url(url):
    """
    Normalize a URL by removing fragments, trailing slashes, and standardizing the format.
    This ensures that URLs like 'https://example.com/' and 'https://example.com' are treated as the same.
    
    Args:
        url: URL string to normalize
    
    Returns:
        Normalized URL string
    """
    try:
        parsed = urlparse(url)
        # Remove fragment (#section) and normalize path
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',  # Remove trailing slash but keep single /
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        return normalized
    except Exception:
        return url

def get_base_domain(domain):
    """
    Extract the base domain from a domain name, removing subdomains.
    
    Args:
        domain: Domain name (e.g., 'www.pleo.io', 'blog.pleo.io')
    
    Returns:
        Base domain (e.g., 'pleo.io')
    
    Example:
        >>> get_base_domain('www.pleo.io')
        'pleo.io'
        >>> get_base_domain('blog.pleo.io')
        'pleo.io'
        >>> get_base_domain('example.co.uk')
        'example.co.uk'
    """
    if not domain:
        return None
    
    # Remove port if present
    domain = domain.split(':')[0]
    
    # Split domain into parts
    parts = domain.split('.')
    
    # Handle common two-part TLDs (e.g., .co.uk, .com.au)
    two_part_tlds = ['co.uk', 'com.au', 'co.nz', 'co.za', 'com.br', 'com.mx']
    
    if len(parts) >= 3:
        # Check if last two parts form a known two-part TLD
        last_two = '.'.join(parts[-2:])
        if last_two in two_part_tlds:
            # For two-part TLDs, base domain is last 3 parts
            return '.'.join(parts[-3:])
    
    # For standard domains, base domain is last 2 parts
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    
    return domain

def _fetch_page(url, session):
    """
    Fetch a single page and extract links.

    Returns:
        Tuple of (url, internal_links, external_links) or (url, None, None) on error
    """
    try:
        response = session.get(url, timeout=10, allow_redirects=True, verify=True)
        response.raise_for_status()

        # Skip non-HTML content early (don't waste time parsing PDFs, images, etc.)
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return (url, [], [])

        if not response.text:
            return (url, [], [])

        # Use lxml parser if available (faster), fall back to html.parser
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception:
            soup = BeautifulSoup(response.text, 'html.parser')

        if not soup:
            return (url, [], [])

        # Extract all href attributes in one pass
        internal_links = []
        external_links = []

        # Get base domain for comparison
        parsed_start = urlparse(url)
        start_base_domain = get_base_domain(parsed_start.netloc)

        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href:
                continue

            try:
                absolute_url = urljoin(url, href)
                parsed = urlparse(absolute_url)

                # Skip non-HTTP(S) links
                if parsed.scheme not in ('http', 'https'):
                    continue

                if not parsed.netloc:
                    continue

                normalized = normalize_url(absolute_url)
                link_base_domain = get_base_domain(parsed.netloc)

                if not link_base_domain:
                    continue

                if link_base_domain == start_base_domain:
                    internal_links.append(normalized)
                else:
                    external_links.append(normalized)
            except Exception:
                continue

        return (url, internal_links, external_links)

    except Exception:
        return (url, [], [])


def crawl_external_links(start_url, max_pages=100, max_workers=5):
    """
    Crawl a website using BFS with concurrent requests and collect external links.

    Uses an iterative approach with a work queue instead of recursion for better
    performance and to avoid stack overflow on deep sites.

    Args:
        start_url: The starting URL to crawl
        max_pages: Maximum number of pages to crawl (default: 100)
        max_workers: Number of concurrent request threads (default: 5)

    Returns:
        Sorted list of unique top-level domains found across all pages

    Example:
        >>> external = crawl_external_links("https://example.com")
        >>> print(external)
        ['facebook.com', 'twitter.com', 'youtube.com', ...]
    """
    # Validate start URL
    try:
        parsed_start = urlparse(start_url)
        start_base_domain = get_base_domain(parsed_start.netloc)
        if not parsed_start.netloc or not start_base_domain:
            return []
    except Exception:
        return []

    visited = set()
    external_links = set()
    queue = deque()

    # Initialize with start URL
    normalized_start = normalize_url(start_url)
    queue.append(normalized_start)
    visited.add(normalized_start)

    session = get_session()

    while queue and len(visited) <= max_pages:
        # Batch URLs for concurrent processing
        batch = []
        while queue and len(batch) < max_workers:
            batch.append(queue.popleft())

        if not batch:
            break

        # Process batch concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_fetch_page, url, session): url for url in batch}

            for future in as_completed(futures):
                try:
                    url, internal_links, found_external = future.result()

                    # Add external links
                    if found_external:
                        external_links.update(found_external)

                    # Queue new internal links
                    if internal_links:
                        for link in internal_links:
                            if link not in visited and len(visited) < max_pages:
                                visited.add(link)
                                queue.append(link)
                except Exception:
                    continue

    # Convert full URLs to unique top-level domains
    return simplify_external_links(external_links)

def simplify_external_links(external_links):
    """
    Simplify a list of external URLs to only contain unique top-level domains.
    Removes subdomains, paths, and duplicates.
    
    Args:
        external_links: List of external URLs
    
    Returns:
        Sorted list of unique top-level domains
    
    Example:
        >>> simplify_external_links(['https://www.google.com/search', 'https://maps.google.com', 'https://example.com'])
        ['example.com', 'google.com']
    """
    unique_domains = set()
    
    for url in external_links:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            if domain:
                # Get base domain (remove subdomains)
                base_domain = get_base_domain(domain)
                if base_domain:
                    unique_domains.add(base_domain)
        except Exception:
            continue
    
    return sorted(list(unique_domains))

#result = crawl_external_links("https://www.microsoft.com")
#simplified_result = simplify_external_links(result)
#print(simplified_result)
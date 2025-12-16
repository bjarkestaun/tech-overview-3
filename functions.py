from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

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

def crawl_external_links(start_url, visited=None, external_links=None):
    """
    Recursively crawl a website starting from a URL and collect all external links.
    Ignores broken links and continues processing.
    
    Args:
        start_url: The starting URL to crawl
        visited: Set of already visited URLs (used internally for recursion)
        external_links: Set of external links found (used internally for recursion)
    
    Returns:
        List of unique external URLs found across all pages and subpages
    
    Example:
        >>> external = crawl_external_links("https://example.com")
        >>> print(external)
        ['https://external-site.com', 'https://another-site.org', ...]
    """
    if visited is None:
        visited = set()
    if external_links is None:
        external_links = set()
    
    # Normalize the URL to handle variations (trailing slashes, fragments, etc.)
    normalized_url = normalize_url(start_url)
    
    # Skip if already visited (check normalized URL)
    if normalized_url in visited:
        return list(external_links)
    
    # Mark as visited immediately to prevent duplicate processing in recursion
    visited.add(normalized_url)
    
    try:
        # Parse the starting URL to get the domain and base domain
        start_parsed = urlparse(start_url)
        start_domain = start_parsed.netloc
        start_base_domain = get_base_domain(start_domain)
        
        if not start_domain or not start_base_domain:
            return list(external_links)
    except Exception as e:
        return list(external_links)
    
    response = None
    try:
        # Fetch the page with headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        response = requests.get(start_url, headers=headers, timeout=10, allow_redirects=True, verify=True)
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        return list(external_links)
    except requests.exceptions.ConnectionError as e:
        return list(external_links)
    except requests.exceptions.HTTPError as e:
        return list(external_links)
    except requests.exceptions.RequestException as e:
        return list(external_links)
    except Exception as e:
        return list(external_links)
    
    # Verify response exists and has content
    if not response or not hasattr(response, 'text'):
        return list(external_links)
    
    try:
        # Parse HTML with error handling
        if not response.text:
            return list(external_links)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links - handle case where soup might be None
        if not soup:
            return list(external_links)
            
        links = soup.find_all('a', href=True)
        
        for link in links:
            try:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Convert relative URLs to absolute URLs
                try:
                    absolute_url = urljoin(start_url, href)
                    # Normalize the absolute URL
                    normalized_absolute_url = normalize_url(absolute_url)
                    parsed_url = urlparse(absolute_url)
                except Exception as e:
                    continue
                
                # Skip non-HTTP(S) links (mailto:, javascript:, etc.)
                if parsed_url.scheme not in ('http', 'https'):
                    continue
                
                # Get the domain of the link
                link_domain = parsed_url.netloc
                
                if not link_domain:
                    continue
                
                # Get the base domain of the link (without subdomains)
                link_base_domain = get_base_domain(link_domain)
                
                if not link_base_domain:
                    continue
                
                # Check if it's external or internal based on base domain
                # Subdomains (e.g., blog.pleo.io) are treated as internal if they share the base domain
                if link_base_domain != start_base_domain:
                    # External link - add to external_links set (use normalized URL)
                    try:
                        external_links.add(normalized_absolute_url)
                    except Exception as e:
                        continue
                else:
                    # Internal link (including subdomains) - check if already visited before crawling
                    if normalized_absolute_url in visited:
                        # Already visited, skip to avoid infinite loops
                        continue
                    
                    # Internal link - recursively crawl it (with error handling)
                    # Limit recursion depth to prevent infinite loops
                    if len(visited) < 100:  # Limit to 100 pages max
                        try:
                            crawl_external_links(normalized_absolute_url, visited, external_links)
                        except RecursionError:
                            continue
                        except Exception as e:
                            continue
                    else:
                        continue
                        
            except Exception as e:
                continue
    
    except Exception as e:
        return list(external_links)
    
    return list(external_links)

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
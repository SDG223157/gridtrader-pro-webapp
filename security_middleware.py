"""
Security Middleware for GridTrader Pro
Provides rate limiting, security headers, and attack detection
"""
import time
import logging
from typing import Dict, Set, Optional
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
import ipaddress

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management with rate limiting and attack detection"""
    
    def __init__(self):
        # Rate limiting storage
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        
        # Attack pattern detection
        self.suspicious_patterns = [
            r'wp-admin',
            r'wordpress',
            r'admin\.php',
            r'config\.php',
            r'setup-config\.php',
            r'\.\./',  # Directory traversal
            r'union.*select',  # SQL injection
            r'<script',  # XSS
            r'javascript:',
            r'eval\(',
            r'base64_decode',
            r'system\(',
            r'exec\(',
            r'passthru\(',
            r'shell_exec\(',
        ]
        self.pattern_regex = re.compile('|'.join(self.suspicious_patterns), re.IGNORECASE)
        
        # Rate limiting configuration
        self.RATE_LIMIT_WINDOW = 60  # 1 minute
        self.MAX_REQUESTS_PER_MINUTE = 200  # Increased for MCP server usage
        self.MAX_404_REQUESTS_PER_MINUTE = 50  # Increased for development/testing
        self.BLOCK_DURATION = 120  # Reduced to 2 minutes
        
        # Whitelist for localhost, health checks, and trusted IPs
        self.whitelisted_ips = {'127.0.0.1', '::1'}
        
        # Additional trusted IP ranges (Cloudflare, common CDNs)
        self.trusted_ip_ranges = [
            '104.16.0.0/12',    # Cloudflare
            '172.64.0.0/13',    # Cloudflare
            '108.162.192.0/18', # Cloudflare
            '198.41.128.0/17',  # Cloudflare
            '173.245.48.0/20',  # Cloudflare
            '103.21.244.0/22',  # Cloudflare
            '103.22.200.0/22',  # Cloudflare
            '103.31.4.0/22',    # Cloudflare
            '141.101.64.0/18',  # Cloudflare
            '188.114.96.0/20',  # Cloudflare
            '190.93.240.0/20',  # Cloudflare
            '197.234.240.0/22', # Cloudflare
            '198.41.128.0/17',  # Cloudflare
        ]
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        if ip in self.whitelisted_ips:
            return True
        
        # Check if it's a private IP (for Docker/internal networks)
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return True
            
            # Check trusted IP ranges (Cloudflare, CDNs)
            for ip_range in self.trusted_ip_ranges:
                if ip_obj in ipaddress.ip_network(ip_range):
                    return True
                    
        except ValueError:
            pass
        
        return False
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip: str, duration: Optional[int] = None):
        """Block an IP for specified duration"""
        if self.is_ip_whitelisted(ip):
            logger.info(f"⚪ Skipping block for whitelisted IP {ip}")
            return
        
        duration = duration or self.BLOCK_DURATION
        self.blocked_ips[ip] = time.time() + duration
        logger.warning(f"🚫 Blocked IP {ip} for {duration} seconds due to suspicious activity")
    
    def unblock_ip(self, ip: str):
        """Manually unblock an IP"""
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            logger.info(f"✅ Manually unblocked IP {ip}")
        
    def clear_all_blocks(self):
        """Clear all blocked IPs (for debugging/reset)"""
        blocked_count = len(self.blocked_ips)
        self.blocked_ips.clear()
        logger.info(f"🧹 Cleared {blocked_count} blocked IPs")
    
    def clean_old_requests(self, ip: str):
        """Remove old requests outside the rate limit window"""
        current_time = time.time()
        window_start = current_time - self.RATE_LIMIT_WINDOW
        
        while self.request_counts[ip] and self.request_counts[ip][0] < window_start:
            self.request_counts[ip].popleft()
    
    def check_rate_limit(self, ip: str, is_404: bool = False, is_authenticated: bool = False) -> bool:
        """Check if request should be rate limited"""
        if self.is_ip_whitelisted(ip):
            return False
        
        if self.is_ip_blocked(ip):
            return True
        
        current_time = time.time()
        self.clean_old_requests(ip)
        
        # Count current requests
        request_count = len(self.request_counts[ip])
        
        # Higher limits for authenticated requests
        max_requests = self.MAX_REQUESTS_PER_MINUTE * 2 if is_authenticated else self.MAX_REQUESTS_PER_MINUTE
        max_404_requests = self.MAX_404_REQUESTS_PER_MINUTE * 2 if is_authenticated else self.MAX_404_REQUESTS_PER_MINUTE
        
        # Check limits
        if is_404 and request_count >= max_404_requests:
            logger.warning(f"⚠️ Rate limit exceeded for 404s from IP {ip}: {request_count} requests (auth: {is_authenticated})")
            self.block_ip(ip)
            return True
        elif request_count >= max_requests:
            logger.warning(f"⚠️ Rate limit exceeded from IP {ip}: {request_count} requests (auth: {is_authenticated})")
            self.block_ip(ip)
            return True
        
        # Record this request
        self.request_counts[ip].append(current_time)
        return False
    
    def detect_attack_patterns(self, url: str, user_agent: str = "") -> bool:
        """Detect common attack patterns in URL and user agent"""
        # Check URL for suspicious patterns
        if self.pattern_regex.search(url):
            return True
        
        # Check for common bot/scanner user agents
        suspicious_agents = [
            'sqlmap', 'nikto', 'dirb', 'gobuster', 'wpscan', 'nmap',
            'masscan', 'zap', 'burp', 'acunetix', 'nessus'
        ]
        
        user_agent_lower = user_agent.lower()
        for agent in suspicious_agents:
            if agent in user_agent_lower:
                return True
        
        return False

# Global security manager instance
security_manager = SecurityManager()

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check if request is authenticated (has valid Bearer token)
        is_authenticated = self.is_request_authenticated(request)
        
        # Check if request should be blocked
        if security_manager.check_rate_limit(client_ip, is_authenticated=is_authenticated):
            logger.warning(f"🚫 Rate limited request from {client_ip} to {request.url.path} (auth: {is_authenticated})")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Please try again later."}
            )
        
        # Process request
        response = await call_next(request)
        
        # Update rate limiting based on response status
        if response.status_code == 404:
            # Check if this IP is making too many 404 requests
            security_manager.check_rate_limit(client_ip, is_404=True, is_authenticated=is_authenticated)
        
        return response
    
    def is_request_authenticated(self, request: Request) -> bool:
        """Check if request has valid authentication"""
        auth_header = request.headers.get("authorization")
        return bool(auth_header and auth_header.startswith("Bearer "))
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (common in reverse proxy setups)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else '127.0.0.1'

class AttackDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect and block common attack patterns"""
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        url_path = str(request.url.path)
        user_agent = request.headers.get('user-agent', '')
        
        # Skip detection for whitelisted IPs
        if not security_manager.is_ip_whitelisted(client_ip):
            # Detect attack patterns
            if security_manager.detect_attack_patterns(url_path, user_agent):
                logger.warning(
                    f"🛡️ Attack pattern detected from {client_ip}: "
                    f"Path: {url_path}, User-Agent: {user_agent[:100]}"
                )
                
                # Block the IP immediately for attack attempts
                security_manager.block_ip(client_ip, duration=600)  # 10 minutes
                
                return JSONResponse(
                    status_code=403,
                    content={"error": "Forbidden"}
                )
        
        response = await call_next(request)
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else '127.0.0.1'

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add HSTS header if HTTPS (check via headers that indicate HTTPS)
        if (request.headers.get('x-forwarded-proto') == 'https' or 
            request.url.scheme == 'https'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Enhanced CSP (Content Security Policy) - Supports TradingView widgets and CDNs
        # TradingView widgets require:
        # - script-src: for widget JavaScript from s3.tradingview.com and s.tradingview.com
        # - frame-src/child-src: for widget iframes that display charts
        # - connect-src: for real-time data connections including WebSocket (wss://)
        # - img-src: for chart images and icons
        # - worker-src: for background processing in widgets
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://s3.tradingview.com "
                "https://s.tradingview.com "
                "https://cdn.jsdelivr.net "
                "https://cdnjs.cloudflare.com "
                "https://cdn.tailwindcss.com "
                "https://cdn.plot.ly "
                "https://cdn.jsdelivr.net "
                "https:; "
            "style-src 'self' 'unsafe-inline' "
                "https://cdnjs.cloudflare.com "
                "https://fonts.googleapis.com "
                "https:; "
            "img-src 'self' data: blob: "
                "https://s3.tradingview.com "
                "https://s.tradingview.com "
                "https://ui-avatars.com "
                "https:; "
            "font-src 'self' "
                "https://cdnjs.cloudflare.com "
                "https://fonts.gstatic.com "
                "https: data:; "
            "connect-src 'self' "
                "https://s3.tradingview.com "
                "https://s.tradingview.com "
                "https://prodata.tradingview.com "
                "https://symbol-search.tradingview.com "
                "wss://data.tradingview.com "
                "wss://prodata.tradingview.com "
                "https:; "
            "frame-src "
                "https://s.tradingview.com "
                "https://www.tradingview.com "
                "https://charting-library.tradingview.com "
                "https://embed.tradingview.com; "
            "child-src "
                "https://s.tradingview.com "
                "https://www.tradingview.com "
                "https://charting-library.tradingview.com "
                "https://embed.tradingview.com; "
            "worker-src 'self' blob:; "
            "frame-ancestors 'none';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        return response

def setup_security_middleware(app):
    """Setup all security middleware for a FastAPI app"""
    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AttackDetectionMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    
    logger.info("🛡️ Security middleware enabled: Rate limiting, Attack detection, Security headers")

def get_security_status() -> Dict:
    """Get current security status for debugging"""
    current_time = time.time()
    
    # Count active blocks
    active_blocks = 0
    blocked_ips_list = []
    for ip, unblock_time in security_manager.blocked_ips.items():
        if current_time < unblock_time:
            active_blocks += 1
            blocked_ips_list.append({
                "ip": ip,
                "unblock_time": unblock_time,
                "remaining_seconds": int(unblock_time - current_time)
            })
    
    # Get request counts
    active_rate_limits = len([
        ip for ip, requests in security_manager.request_counts.items() 
        if len(requests) > 0
    ])
    
    return {
        "active_blocked_ips": active_blocks,
        "blocked_ips_details": blocked_ips_list,
        "active_rate_limited_ips": active_rate_limits,
        "total_tracked_ips": len(security_manager.request_counts),
        "rate_limit_window": security_manager.RATE_LIMIT_WINDOW,
        "max_requests_per_minute": security_manager.MAX_REQUESTS_PER_MINUTE,
        "max_requests_per_minute_authenticated": security_manager.MAX_REQUESTS_PER_MINUTE * 2,
        "max_404_requests_per_minute": security_manager.MAX_404_REQUESTS_PER_MINUTE,
        "max_404_requests_per_minute_authenticated": security_manager.MAX_404_REQUESTS_PER_MINUTE * 2,
        "block_duration": security_manager.BLOCK_DURATION,
        "whitelisted_ips": list(security_manager.whitelisted_ips),
        "trusted_ip_ranges": security_manager.trusted_ip_ranges
    }

# Utility functions for debugging/management
def clear_rate_limits():
    """Clear all rate limiting data (for debugging)"""
    security_manager.clear_all_blocks()
    security_manager.request_counts.clear()
    logger.info("🧹 Cleared all rate limiting data")

def unblock_ip(ip: str):
    """Manually unblock a specific IP"""
    security_manager.unblock_ip(ip)

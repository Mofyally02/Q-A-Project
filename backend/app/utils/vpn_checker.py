import asyncio
import logging
from typing import List, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class VPNChecker:
    """Service for checking if an IP address is from a VPN/proxy"""
    
    def __init__(self):
        self.vpn_providers = [
            "vpn", "proxy", "tor", "anonymizer", "hide", "mask", "shield",
            "guard", "protect", "secure", "private", "anonymous", "incognito"
        ]
        
        # Known VPN/proxy IP ranges (simplified - in production, use a proper service)
        self.known_vpn_ranges = [
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
            "127.0.0.0/8"
        ]
    
    async def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """Check if an IP address is from a VPN/proxy"""
        try:
            # Check against known VPN ranges
            if self._is_private_ip(ip_address):
                return {
                    "is_vpn": True,
                    "confidence": 0.9,
                    "reason": "Private IP address",
                    "provider": "Private Network"
                }
            
            # Check against external VPN detection services
            vpn_result = await self._check_external_services(ip_address)
            if vpn_result:
                return vpn_result
            
            # Basic heuristics
            heuristic_result = await self._check_heuristics(ip_address)
            if heuristic_result:
                return heuristic_result
            
            return {
                "is_vpn": False,
                "confidence": 0.1,
                "reason": "No VPN indicators found",
                "provider": None
            }
            
        except Exception as e:
            logger.error(f"Error checking IP {ip_address}: {e}")
            return {
                "is_vpn": False,
                "confidence": 0.0,
                "reason": "Error during check",
                "provider": None
            }
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is in private ranges"""
        try:
            import ipaddress
            
            ip = ipaddress.ip_address(ip_address)
            
            for range_str in self.known_vpn_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking private IP: {e}")
            return False
    
    async def _check_external_services(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Check against external VPN detection services"""
        try:
            # Example: Check against a free VPN detection API
            # In production, you would use a proper service like IPQualityScore, etc.
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Example API call (replace with actual service)
                response = await client.get(
                    f"https://api.example.com/vpn-check/{ip_address}",
                    headers={"User-Agent": "AL-Tech-Academy/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("is_vpn", False):
                        return {
                            "is_vpn": True,
                            "confidence": data.get("confidence", 0.8),
                            "reason": data.get("reason", "Detected by external service"),
                            "provider": data.get("provider", "Unknown")
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking external services: {e}")
            return None
    
    async def _check_heuristics(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Check using basic heuristics"""
        try:
            # Check if IP is in known VPN ranges
            if self._is_known_vpn_range(ip_address):
                return {
                    "is_vpn": True,
                    "confidence": 0.7,
                    "reason": "IP in known VPN range",
                    "provider": "Heuristic Detection"
                }
            
            # Check reverse DNS
            reverse_dns = await self._check_reverse_dns(ip_address)
            if reverse_dns and self._is_vpn_hostname(reverse_dns):
                return {
                    "is_vpn": True,
                    "confidence": 0.6,
                    "reason": f"VPN hostname detected: {reverse_dns}",
                    "provider": "DNS Heuristic"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in heuristic check: {e}")
            return None
    
    def _is_known_vpn_range(self, ip_address: str) -> bool:
        """Check if IP is in known VPN ranges"""
        # This would be expanded with actual VPN IP ranges
        # For now, just check for common patterns
        return False
    
    async def _check_reverse_dns(self, ip_address: str) -> Optional[str]:
        """Check reverse DNS for the IP address"""
        try:
            import socket
            
            # Set timeout for DNS lookup
            socket.setdefaulttimeout(5)
            
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname.lower()
            
        except Exception as e:
            logger.debug(f"Reverse DNS lookup failed for {ip_address}: {e}")
            return None
    
    def _is_vpn_hostname(self, hostname: str) -> bool:
        """Check if hostname indicates VPN usage"""
        if not hostname:
            return False
        
        hostname_lower = hostname.lower()
        
        # Check for VPN-related keywords
        for keyword in self.vpn_providers:
            if keyword in hostname_lower:
                return True
        
        # Check for common VPN patterns
        vpn_patterns = [
            "vpn-", "proxy-", "tor-", "anonymizer-",
            "hide-", "mask-", "shield-", "guard-",
            "protect-", "secure-", "private-", "anonymous-"
        ]
        
        for pattern in vpn_patterns:
            if pattern in hostname_lower:
                return True
        
        return False
    
    async def check_user_ip(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Check if user's IP is from VPN and log if necessary"""
        try:
            vpn_result = await self.check_ip(ip_address)
            
            if vpn_result["is_vpn"]:
                logger.warning(f"VPN detected for user {user_id}: {vpn_result}")
                
                # In a real implementation, you would log this to the database
                # and potentially take action based on your policy
                
                return {
                    "blocked": True,
                    "reason": "VPN/Proxy detected",
                    "details": vpn_result
                }
            
            return {
                "blocked": False,
                "reason": "IP check passed",
                "details": vpn_result
            }
            
        except Exception as e:
            logger.error(f"Error checking user IP: {e}")
            return {
                "blocked": False,
                "reason": "Error during check",
                "details": {"error": str(e)}
            }
    
    async def get_ip_info(self, ip_address: str) -> Dict[str, Any]:
        """Get additional information about an IP address"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Example: Get IP geolocation info
                response = await client.get(
                    f"https://ipapi.co/{ip_address}/json/",
                    headers={"User-Agent": "AL-Tech-Academy/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "ip": data.get("ip"),
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country_name"),
                        "country_code": data.get("country_code"),
                        "timezone": data.get("timezone"),
                        "org": data.get("org"),
                        "asn": data.get("asn")
                    }
            
            return {"ip": ip_address, "error": "Could not fetch IP info"}
            
        except Exception as e:
            logger.error(f"Error getting IP info: {e}")
            return {"ip": ip_address, "error": str(e)}

import re
from typing import Optional

class DescriptionParser:
    @staticmethod
    def parse(description: str, name: str):
        brand = name.split()[0] if name else None

        screen_inches = DescriptionParser._extract_screen_size(description)
        ram_gb = DescriptionParser._extract_ram(description)
        storage_gb = DescriptionParser._extract_storage(description)
        cpu = DescriptionParser._extract_cpu(description)
        os = DescriptionParser._extract_os(description)

        return {
            "brand": brand,
            "screen_inches": screen_inches,
            "ram_gb": ram_gb,
            "storage_gb": storage_gb,
            "cpu": cpu,
            "os": os,
        }

    @staticmethod
    def _extract_screen_size(text: str) -> Optional[float]:
        # Matches patterns like 14", 15.6″, etc.
        match = re.search(r'(\d{1,2}(?:\.\d+)?)\s*[″"]', text)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def _extract_ram(text: str) -> Optional[int]:
        match = re.search(r'(\d+)\s*gb\s*(ram|ddr\d*|ddr\dL)?', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _extract_storage(text: str) -> Optional[int]:
        total = 0
        for match in re.finditer(r'(\d+)\s*(gb|tb)(\s*(ssd|hdd|emmc|ssh[d]?))?', text, re.IGNORECASE):
            value, unit = int(match.group(1)), match.group(2).lower()
            if unit == 'tb':
                value *= 1024
            total += value
        return total if total else None

    @staticmethod
    def _extract_cpu(text: str) -> Optional[str]:
        # Match keywords and take surrounding context
        match = re.search(r'((?:intel|amd|apple|core\s*i\d|i\d|celeron|pentium|ryzen|snapdragon)[^,]*)', text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_os(text: str) -> Optional[str]:
        os_patterns = [
            r'windows\s+\d+(?:\s+\w+)*(?:\s*\+\s*\w+.*)?',  # Windows 10 Home, Windows 10 Pro + Office
            r'win\d?\s*pro\s*\d*bit',                       # Win7 Pro 64bit
            r'freedos',
            r'endless\s+os',
            r'no\s+os',
            r'macos',
            r'linux',
            r'dos\b',
            r'android',
            r'ios',
        ]
        for pattern in os_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

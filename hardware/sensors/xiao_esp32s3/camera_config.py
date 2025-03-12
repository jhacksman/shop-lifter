"""
Configuration options for the OV2640 camera.

This module provides configuration presets for different
resolutions and quality settings for the OV2640 camera.
"""

from enum import Enum
from typing import Dict, Any


class CameraResolution(Enum):
    """Supported camera resolutions."""
    QQVGA = (160, 120)
    QVGA = (320, 240)
    VGA = (640, 480)
    SVGA = (800, 600)
    XGA = (1024, 768)
    SXGA = (1280, 1024)
    UXGA = (1600, 1200)


def get_camera_config(resolution: CameraResolution, jpeg_quality: int = 12) -> Dict[str, Any]:
    """
    Get camera configuration for the specified resolution and quality.
    
    Args:
        resolution: Camera resolution from CameraResolution enum
        jpeg_quality: JPEG quality (0-63, lower is better quality)
        
    Returns:
        Dictionary with camera configuration parameters
    """
    width, height = resolution.value
    
    config = {
        "ledc_channel": 0,
        "ledc_timer": 0,
        "pin_xclk": 10,
        "pin_sccb_sda": 40,
        "pin_sccb_scl": 39,
        "pin_d7": 48,
        "pin_d6": 11,
        "pin_d5": 12,
        "pin_d4": 14,
        "pin_d3": 16,
        "pin_d2": 18,
        "pin_d1": 17,
        "pin_d0": 15,
        "pin_vsync": 38,
        "pin_href": 47,
        "pin_pclk": 13,
        "xclk_freq_hz": 20000000,
        "pixel_format": 2,  # PIXFORMAT_JPEG
        "frame_size": get_frame_size_value(width, height),
        "jpeg_quality": jpeg_quality,
        "fb_count": 2
    }
    
    return config


def get_frame_size_value(width: int, height: int) -> int:
    """
    Convert resolution dimensions to frame size value.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Frame size value for the ESP32 camera driver
    """
    # Frame size values for ESP32 camera driver
    frame_sizes = {
        (160, 120): 0,    # FRAMESIZE_QQVGA
        (320, 240): 1,    # FRAMESIZE_QVGA
        (640, 480): 2,    # FRAMESIZE_VGA
        (800, 600): 3,    # FRAMESIZE_SVGA
        (1024, 768): 4,   # FRAMESIZE_XGA
        (1280, 1024): 5,  # FRAMESIZE_SXGA
        (1600, 1200): 6   # FRAMESIZE_UXGA
    }
    
    return frame_sizes.get((width, height), 1)  # Default to QVGA if not found

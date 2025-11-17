"""
Configuration settings for the broadband AI scraping pipeline
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Source URLs
SOURCES = {
    "thinkbroadband": {
        "name": "thinkBroadband News Archive",
        "base_url": "https://www.thinkbroadband.com",
        "news_url": "https://www.thinkbroadband.com/news",
        "enabled": True
    },
    "fibrenews": {
        "name": "Fibre News",
        "base_url": "https://www.fibrenews.co.uk",
        "news_url": "https://www.fibrenews.co.uk/news",
        "enabled": True
    },
    "ispreview": {
        "name": "ISPreview UK",
        "base_url": "https://www.ispreview.co.uk",
        "news_url": "https://www.ispreview.co.uk/index.php/category/news",
        "enabled": True
    }
}

# AI-related keywords to search for
AI_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "machine learning",
    "ML",
    "deep learning",
    "neural network",
    "automation",
    "chatbot",
    "predictive analytics",
    "intelligent",
    "algorithm",
    "generative AI",
    "GenAI",
    "large language model",
    "LLM"
]

# AI use case categories
AI_USE_CASES = {
    "network_optimization": [
        "network optimization", "bandwidth", "traffic management",
        "routing", "capacity planning", "network performance",
        "infrastructure optimization", "spectrum management"
    ],
    "customer_support": [
        "customer support", "customer service", "chatbot",
        "virtual assistant", "help desk", "customer experience",
        "call center", "support automation"
    ],
    "predictive_maintenance": [
        "predictive maintenance", "fault prediction", "network monitoring",
        "anomaly detection", "preventive maintenance", "outage prediction",
        "equipment failure", "proactive maintenance"
    ],
    "marketing_automation": [
        "marketing", "personalization", "recommendation",
        "targeted advertising", "customer segmentation", "campaign",
        "lead generation", "content optimization"
    ],
    "security": [
        "security", "threat detection", "cybersecurity", "fraud detection",
        "intrusion detection", "vulnerability", "attack prevention"
    ],
    "analytics": [
        "analytics", "data analysis", "insights", "business intelligence",
        "reporting", "metrics", "visualization", "forecasting"
    ]
}

# Scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2  # seconds
MAX_RETRIES = 3

# Analysis settings
MIN_CONFIDENCE_SCORE = 0.3
SENTIMENT_ENABLED = True

# Output settings
OUTPUT_FORMATS = ["json", "csv"]
OUTPUT_FILENAME_PREFIX = "broadband_ai_analysis"

Pinterest Media Scraper - Quick Start

Overview

This Python script uses Playwright to scrape high-quality images from Pinterest boards. It is divided into two phases:

Gather Pin Links: Logs into Pinterest using cookies, collects all pin URLs from a given board link, and saves them.

Download Media: Visits each pin URL, clicks to view the high-quality version, and downloads it.

Usage

Export Pinterest Cookies: Use a Chrome extension like "EditThisCookie" to export cookies to pinterest_cookies.json.

Run the Script:

Phase 1: Collect all pin links.

Phase 2: Download high-quality media.

Requirements

Python

Playwright

Pinterest account cookies

Notes

Ensure cookies are exported correctly.

The script scrolls through the page to load all pins.


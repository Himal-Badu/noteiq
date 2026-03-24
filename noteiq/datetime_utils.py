"""
Date and time utilities for NoteIQ
Provides helpers for date formatting, parsing, and calculations
"""
from datetime import datetime, timedelta, date
from typing import Optional, Union
import re


def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a datetime object.
    
    Args:
        dt: Datetime to format
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object with time.
    
    Args:
        dt: Datetime to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").
    
    Args:
        dt: Datetime to format
        
    Returns:
        Relative time string
    """
    if dt is None:
        return "Unknown"
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Try ISO format first
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def parse_relative_date(date_str: str) -> Optional[datetime]:
    """
    Parse relative date string (e.g., "today", "tomorrow", "next week").
    
    Args:
        date_str: Relative date string
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    now = datetime.utcnow()
    
    if date_str in ["today", "now"]:
        return now
    elif date_str == "tomorrow":
        return now + timedelta(days=1)
    elif date_str == "yesterday":
        return now - timedelta(days=1)
    elif date_str == "next week":
        return now + timedelta(weeks=1)
    elif date_str == "last week":
        return now - timedelta(weeks=1)
    elif date_str == "next month":
        return now + timedelta(days=30)
    elif date_str == "last month":
        return now - timedelta(days=30)
    elif date_str == "next year":
        return now + timedelta(days=365)
    elif date_str == "last year":
        return now - timedelta(days=365)
    
    # Try parsing as offset (e.g., "+3d", "-2w")
    match = re.match(r'^([+-]?)(\d+)([dwmy])$', date_str)
    if match:
        sign = 1 if match.group(1) == "+" else -1
        amount = int(match.group(2))
        unit = match.group(3)
        
        if unit == "d":
            delta = timedelta(days=amount)
        elif unit == "w":
            delta = timedelta(weeks=amount)
        elif unit == "m":
            delta = timedelta(days=amount * 30)
        elif unit == "y":
            delta = timedelta(days=amount * 365)
        else:
            return None
        
        return now + (sign * delta)
    
    return None


def is_overdue(due_date: datetime) -> bool:
    """
    Check if a due date has passed.
    
    Args:
        due_date: Due date to check
        
    Returns:
        True if overdue
    """
    if due_date is None:
        return False
    return datetime.utcnow() > due_date


def is_due_today(due_date: datetime) -> bool:
    """
    Check if a due date is today.
    
    Args:
        due_date: Due date to check
        
    Returns:
        True if due today
    """
    if due_date is None:
        return False
    return due_date.date() == datetime.utcnow().date()


def is_due_soon(due_date: datetime, days: int = 3) -> bool:
    """
    Check if a due date is within the specified days.
    
    Args:
        due_date: Due date to check
        days: Number of days to consider "soon"
        
    Returns:
        True if due soon
    """
    if due_date is None:
        return False
    now = datetime.utcnow()
    return now < due_date <= now + timedelta(days=days)


def get_date_range(start: datetime, end: datetime) -> int:
    """
    Get number of days in a date range.
    
    Args:
        start: Start date
        end: End date
        
    Returns:
        Number of days
    """
    if start is None or end is None:
        return 0
    return (end - start).days


def get_week_range(dt: Optional[datetime] = None) -> tuple:
    """
    Get the start and end of the week for a given date.
    
    Args:
        dt: Date to get week for (defaults to now)
        
    Returns:
        Tuple of (start, end) datetime
    """
    if dt is None:
        dt = datetime.utcnow()
    
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    
    return start, end


def get_month_range(dt: Optional[datetime] = None) -> tuple:
    """
    Get the start and end of the month for a given date.
    
    Args:
        dt: Date to get month for (defaults to now)
        
    Returns:
        Tuple of (start, end) datetime
    """
    if dt is None:
        dt = datetime.utcnow()
    
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if dt.month == 12:
        end = dt.replace(year=dt.year + 1, month=1, day=1) - timedelta(seconds=1)
    else:
        end = dt.replace(month=dt.month + 1, day=1) - timedelta(seconds=1)
    
    return start, end


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h"
    else:
        days = int(seconds / 86400)
        return f"{days}d"


def estimate_reading_time(text: str, words_per_minute: int = 225) -> int:
    """
    Estimate reading time in minutes.
    
    Args:
        text: Text to estimate
        words_per_minute: Reading speed
        
    Returns:
        Estimated minutes
    """
    words = len(text.split())
    minutes = max(1, round(words / words_per_minute))
    return minutes

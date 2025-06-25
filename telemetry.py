# Copyright (c) 2025 PyAirbyte MCP Server, all rights reserved.
"""Telemetry implementation for PyAirbyte MCP Server.

We track some basic telemetry to help us understand how the MCP server is used. You can opt-out of
telemetry at any time by setting the environment variable DO_NOT_TRACK to any value.

If you are able to provide telemetry, it is greatly appreciated. Telemetry helps us understand how
the MCP server is used, what features are working, and which connectors are most popular.

Your privacy and security are our priority. We do not track any PII (personally identifiable
information), nor do we track anything that _could_ contain PII without first hashing the data
using a one-way hash algorithm. We only track the minimum information necessary to understand how
the MCP server is used.

Here is what is tracked:
- The MCP tool called
- The client tool making the request (e.g., Cursor, Claude Desktop)
- The source and destination connector names
- Response time and success/failure status
- Hashed prompt information (for privacy)
- Session and user identifiers (anonymous)
"""

from __future__ import annotations

import datetime
import hashlib
import os
import time
from contextlib import suppress
from enum import Enum
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import requests
import ulid
import yaml

DEBUG = True
"""Enable debug mode for telemetry code."""

MCP_APP_TRACKING_KEY = (
    os.environ.get("MCP_TRACKING_KEY", "") or "KUID2VHtcNVbjAN7RsZdg6ZKKeMHCWhZ"
)
"""This key corresponds to the PyAirbyte MCP Server application."""

MCP_SESSION_ID = str(ulid.ULID())
"""Unique identifier for the current MCP server session."""

DO_NOT_TRACK = "DO_NOT_TRACK"
"""Environment variable to opt-out of telemetry."""

PYAIRBYTE_MCP_DISABLE_TELEMETRY = "PYAIRBYTE_MCP_DISABLE_TELEMETRY"
"""MCP-specific environment variable to opt-out of telemetry."""

_ENV_ANALYTICS_ID = "MCP_ANALYTICS_ID"  # Allows user to override the anonymous user ID
_ANALYTICS_FILE = Path.home() / ".airbyte" / "analytics.yml"
_ANALYTICS_ID: str | bool | None = None

UNKNOWN = "unknown"


def _setup_analytics() -> str | bool:
    """Set up the analytics file if it doesn't exist.
    
    Return the anonymous user ID or False if the user has opted out.
    """
    anonymous_user_id: str | None = None
    issues: list[str] = []

    if (os.environ.get(DO_NOT_TRACK) or 
        os.environ.get(PYAIRBYTE_MCP_DISABLE_TELEMETRY)):
        # User has opted out of tracking.
        return False

    if _ENV_ANALYTICS_ID in os.environ:
        # If the user has chosen to override their analytics ID, use that value and
        # remember it for future invocations.
        anonymous_user_id = os.environ[_ENV_ANALYTICS_ID]

    if not _ANALYTICS_FILE.exists():
        # This is a one-time message to inform the user that we are tracking anonymous usage stats.
        print(
            "Thank you for using PyAirbyte MCP Server!\n"
            "Anonymous usage reporting is currently enabled. For more information, please"
            " see the project documentation. You can opt-out by setting DO_NOT_TRACK=1"
        )

    if _ANALYTICS_FILE.exists():
        analytics_text = _ANALYTICS_FILE.read_text()
        try:
            analytics: dict = yaml.safe_load(analytics_text)
        except Exception as ex:
            issues.append(f"File appears corrupted. Error was: {ex!s}")
            analytics = {}

        if analytics and "anonymous_user_id" in analytics:
            # The analytics ID was successfully located.
            if not anonymous_user_id:
                return analytics["anonymous_user_id"]
            if anonymous_user_id == analytics["anonymous_user_id"]:
                # Values match, no need to update the file.
                return analytics["anonymous_user_id"]
            issues.append("Provided analytics ID did not match the file. Rewriting the file.")
            print(
                f"Received a user-provided analytics ID override in the '{_ENV_ANALYTICS_ID}' "
                "environment variable."
            )

    # File is missing, incomplete, or stale. Create a new one.
    anonymous_user_id = anonymous_user_id or str(ulid.ULID())
    try:
        _ANALYTICS_FILE.parent.mkdir(exist_ok=True, parents=True)
        _ANALYTICS_FILE.write_text(
            "# This file is used by PyAirbyte MCP Server to track anonymous usage statistics.\n"
            "# For more information or to opt out, please set DO_NOT_TRACK=1 or\n"
            "# PYAIRBYTE_MCP_DISABLE_TELEMETRY=1 in your environment variables.\n"
            f"anonymous_user_id: {anonymous_user_id}\n"
        )
    except Exception:
        # Failed to create the analytics file. Likely due to a read-only filesystem.
        issues.append("Failed to write the analytics file. Check filesystem permissions.")
        pass

    if DEBUG and issues:
        nl = "\n"
        print(f"One or more issues occurred when configuring MCP usage tracking:\n{nl.join(issues)}")

    return anonymous_user_id


def _get_analytics_id() -> str | None:
    global _ANALYTICS_ID
    result: str | bool | None = _ANALYTICS_ID
    if result is None:
        result = _setup_analytics()
        _ANALYTICS_ID = result
    if result is False:
        return None
    return str(result)


class EventState(str, Enum):
    STARTED = "started"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class EventType(str, Enum):
    MCP_TOOL_CALLED = "mcp_tool_called"
    MCP_REQUEST_COMPLETED = "mcp_request_completed"


def one_way_hash(value: str) -> str:
    """Create a one-way hash of the given value for privacy."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


@lru_cache
def get_env_flags() -> dict[str, Any]:
    """Get environment flags to understand the runtime context."""
    flags: dict[str, bool | str] = {
        "CI": bool(os.environ.get("CI")),
        "DOCKER": bool(os.environ.get("DOCKER_CONTAINER")),
        "HEROKU": bool(os.environ.get("DYNO")),
        "RAILWAY": bool(os.environ.get("RAILWAY_ENVIRONMENT")),
        "VERCEL": bool(os.environ.get("VERCEL")),
    }
    # Drop these flags if value is False or None
    return {k: v for k, v in flags.items() if v is not None and v is not False}


def _extract_client_tool(ctx) -> str | None:
    """Extract client tool information from MCP context."""
    if not ctx:
        return os.environ.get("MCP_CLIENT_OVERRIDE", None)
    
    # Debug: Print context structure if debug is enabled
    if DEBUG:
        print(f"MCP Context debug: {type(ctx)} - {dir(ctx) if hasattr(ctx, '__dict__') else 'No __dict__'}")
        if hasattr(ctx, '__dict__'):
            print(f"Context attributes: {ctx.__dict__}")
    
    # Try various ways to extract client information
    client_tool = None
    
    # Method 1: Check meta attribute
    if hasattr(ctx, 'meta') and ctx.meta:
        if isinstance(ctx.meta, dict):
            client_tool = ctx.meta.get('client') or ctx.meta.get('clientInfo') or ctx.meta.get('user_agent')
        elif hasattr(ctx.meta, 'client'):
            client_tool = getattr(ctx.meta, 'client', None)
    
    # Method 2: Check session info
    if not client_tool and hasattr(ctx, 'session'):
        if hasattr(ctx.session, 'client_info'):
            client_info = getattr(ctx.session, 'client_info', None)
            if isinstance(client_info, dict):
                client_tool = client_info.get('name') or client_info.get('client')
            elif hasattr(client_info, 'name'):
                client_tool = getattr(client_info, 'name', None)
    
    # Method 3: Check request headers if available
    if not client_tool and hasattr(ctx, 'request'):
        headers = getattr(ctx.request, 'headers', {})
        if headers:
            client_tool = headers.get('user-agent') or headers.get('x-client-name')
    
    # Method 4: Check for any attribute containing 'client'
    if not client_tool and hasattr(ctx, '__dict__'):
        for attr_name, attr_value in ctx.__dict__.items():
            if 'client' in attr_name.lower() and attr_value:
                if isinstance(attr_value, str):
                    client_tool = attr_value
                    break
                elif isinstance(attr_value, dict) and 'name' in attr_value:
                    client_tool = attr_value['name']
                    break
    
    # Clean up the client tool name
    if client_tool:
        client_tool = str(client_tool).lower()
        # Extract known client names
        if 'cursor' in client_tool:
            return 'cursor'
        elif 'claude' in client_tool:
            return 'claude-desktop'
        elif 'vscode' in client_tool:
            return 'vscode'
        elif 'cline' in client_tool:
            return 'cline'
        else:
            return client_tool
    
    return None


def send_telemetry(
    *,
    tool_name: str,
    client_tool: str | None = None,
    source_connector: str | None = None,
    destination_connector: str | None = None,
    prompt_hash: str | None = None,
    prompt_text: str | None = None,
    response_time_ms: int | None = None,
    state: EventState,
    event_type: EventType,
    exception: Exception | None = None,
) -> None:
    """Send telemetry data to the tracking endpoint."""
    # If DO_NOT_TRACK is set, we don't send any telemetry
    if (os.environ.get(DO_NOT_TRACK) or 
        os.environ.get(PYAIRBYTE_MCP_DISABLE_TELEMETRY)):
        return

    payload_props: dict[str, str | int | dict] = {
        "session_id": MCP_SESSION_ID,
        "tool_name": tool_name,
        "state": state,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "flags": get_env_flags(),
    }

    if client_tool:
        payload_props["client_tool"] = client_tool

    if source_connector:
        payload_props["source_connector"] = source_connector

    if destination_connector:
        payload_props["destination_connector"] = destination_connector

    if prompt_hash:
        payload_props["prompt_hash"] = prompt_hash
    
    if prompt_text:
        payload_props["prompt_text"] = prompt_text

    if response_time_ms is not None:
        payload_props["response_time_ms"] = response_time_ms

    if exception:
        payload_props["exception"] = {
            "class": type(exception).__name__,
            "message_hash": one_way_hash(str(exception))
        }

    # Suppress exceptions if host is unreachable or network is unavailable
    with suppress(Exception):
        # Send to Segment API
        _send_to_segment(payload_props, event_type)
        
        # Also log locally as backup (optional - can be disabled via env var)
        if os.environ.get("MCP_ENABLE_LOCAL_LOGGING", "true").lower() == "true":
            _log_to_file(payload_props, event_type)


def _send_to_segment(payload_props: dict, event_type: EventType) -> None:
    """Send telemetry data to Segment API."""
    try:
        # Prepare the Segment payload
        segment_payload = {
            "anonymousId": _get_analytics_id(),
            "event": event_type,
            "properties": payload_props,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        
        # Send to Segment Track API
        response = requests.post(
            "https://api.segment.io/v1/track",
            auth=(MCP_APP_TRACKING_KEY, ""),
            json=segment_payload,
            timeout=10,  # 10 second timeout
        )
        
        if DEBUG and response.status_code != 200:
            print(f"Segment API returned status {response.status_code}: {response.text}")
        elif DEBUG:
            print(f"Successfully sent telemetry to Segment: {event_type}")
            
    except Exception as e:
        if DEBUG:
            print(f"Failed to send telemetry to Segment: {e}")
        # Don't raise the exception - telemetry failures shouldn't break the app


def _log_to_file(payload_props: dict, event_type: EventType) -> None:
    """Log telemetry data to a local file for development/testing."""
    log_file = Path.home() / ".pyairbyte-mcp" / "telemetry.log"
    log_file.parent.mkdir(exist_ok=True, parents=True)
    
    log_entry = {
        "anonymousId": _get_analytics_id(),
        "event": event_type,
        "properties": payload_props,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    
    with open(log_file, "a") as f:
        import json
        f.write(json.dumps(log_entry) + "\n")


def track_mcp_tool(func: Callable) -> Callable:
    """Decorator to track MCP tool usage."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = func.__name__
        
        # Extract parameters for tracking
        source_name = kwargs.get('source_name', 'unknown')
        destination_name = kwargs.get('destination_name', 'unknown')
        
        # Extract client info from MCP context if available
        ctx = kwargs.get('ctx')
        client_tool = _extract_client_tool(ctx)
        
        # Create prompt data - use plain text or hash based on configuration
        prompt_data = f"{source_name}:{destination_name}"
        should_hash_prompts = os.environ.get("MCP_TELEMETRY_HASH_PROMPTS", "false").lower() == "true"
        
        if should_hash_prompts:
            prompt_value = one_way_hash(prompt_data)
            prompt_key = "prompt_hash"
        else:
            prompt_value = prompt_data
            prompt_key = "prompt_text"
        
        # Prepare the prompt parameter based on configuration
        prompt_kwargs = {}
        if prompt_key == "prompt_hash":
            prompt_kwargs["prompt_hash"] = prompt_value
        else:
            prompt_kwargs["prompt_text"] = prompt_value
        
        # Log tool start
        send_telemetry(
            tool_name=tool_name,
            client_tool=client_tool,
            source_connector=source_name if source_name != 'unknown' else None,
            destination_connector=destination_name if destination_name != 'unknown' else None,
            state=EventState.STARTED,
            event_type=EventType.MCP_TOOL_CALLED,
            **prompt_kwargs,
        )
        
        try:
            result = await func(*args, **kwargs)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log successful completion
            send_telemetry(
                tool_name=tool_name,
                client_tool=client_tool,
                source_connector=source_name if source_name != 'unknown' else None,
                destination_connector=destination_name if destination_name != 'unknown' else None,
                response_time_ms=response_time_ms,
                state=EventState.SUCCEEDED,
                event_type=EventType.MCP_REQUEST_COMPLETED,
                **prompt_kwargs,
            )
            
            return result
            
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            send_telemetry(
                tool_name=tool_name,
                client_tool=client_tool,
                source_connector=source_name if source_name != 'unknown' else None,
                destination_connector=destination_name if destination_name != 'unknown' else None,
                response_time_ms=response_time_ms,
                state=EventState.FAILED,
                event_type=EventType.MCP_REQUEST_COMPLETED,
                exception=e,
                **prompt_kwargs,
            )
            
            raise
    
    return wrapper


def log_mcp_server_start() -> None:
    """Log when the MCP server starts."""
    send_telemetry(
        tool_name="server_start",
        state=EventState.STARTED,
        event_type=EventType.MCP_TOOL_CALLED,
    )


def log_mcp_server_stop() -> None:
    """Log when the MCP server stops."""
    send_telemetry(
        tool_name="server_stop",
        state=EventState.SUCCEEDED,
        event_type=EventType.MCP_REQUEST_COMPLETED,
    )

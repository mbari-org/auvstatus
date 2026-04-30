from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, TypeVar

from tethysdash_models import (
	ChartDataElement,
	DeploymentInfo,
	DeploymentResponse,
	Event,
	ScriptDescriptionResponse,
	WaypointInfo,
	WpInfoResponse,
	WpMissionDescription,
)

EventT = TypeVar("EventT", bound=Event)

EVENTS_TIMEOUT = 12
NEWSTYLE_TIMEOUT = 8
EARLIEST_FROM_MS = 1234567890123  # legacy floor for the events `from` param


class TethysDashClient:
	def __init__(self, server: str, vehicle: str, *, debug: bool = False) -> None:
		self.server = server
		self.vehicle = vehicle
		self.debug = debug
		self._scheme = (
			"http" if ("tethysdash" in server or "localhost" in server) else "https"
		)

	def _url(self, path: str, query: str = "") -> str:
		base = f"{self._scheme}://{self.server}/TethysDash/api/{path}"
		return f"{base}?{query}" if query else base

	def _get(self, url: str, *, timeout: int) -> Optional[bytes]:
		if self.debug:
			print(f"### QUERY: {url}", file=sys.stderr)
		try:
			with urllib.request.urlopen(url, timeout=timeout) as response:
				return response.read()
		except urllib.error.HTTPError as exc:
			if self.debug:
				print(f"### HTTP ERROR: {url}: {exc}", file=sys.stderr)
			return None

	# --- typed endpoints ---

	def events(
		self,
		event_class: type[EventT] = Event,  # type: ignore[assignment]
		*,
		event_types: Optional[str] = None,
		name: Optional[str] = None,
		text_matches: Optional[str] = None,
		limit: Optional[object] = None,
		after_ms: Optional[int] = None,
	) -> Optional[list[EventT]]:
		# If a typed Event subclass is passed and the caller didn't override
		# `event_types`, derive the query parameter from the class's Literal
		# event_type so call site and parser stay in sync.
		if event_types is None:
			event_types = event_class.event_type_literal()
		if after_ms is None or int(after_ms) < EARLIEST_FROM_MS:
			after_ms = EARLIEST_FROM_MS
		params = {
			"vehicles": self.vehicle,
			"eventTypes": event_types,
			"name": name,
			"text.matches": text_matches,
			"limit": limit,
			"from": after_ms,
		}
		query = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
		raw = self._get(self._url("events", query), timeout=EVENTS_TIMEOUT)
		if raw is None:
			return None
		items = json.loads(raw).get("result") or []
		return [event_class.model_validate(item) for item in items]

	def chart_data(
		self,
		variable: str,
		*,
		max_len: Optional[int] = None,
		from_ms: Optional[int] = None,
	) -> Optional[ChartDataElement]:
		params = {"vehicle": self.vehicle, "maxlen": max_len, "from": from_ms}
		query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
		raw = self._get(self._url(f"data/{variable}", query), timeout=NEWSTYLE_TIMEOUT)
		if raw is None:
			return None
		return ChartDataElement.model_validate_json(raw)

	def last_deployment(self) -> Optional[DeploymentInfo]:
		query = urllib.parse.urlencode({"vehicle": self.vehicle})
		raw = self._get(self._url("deployments/last", query), timeout=NEWSTYLE_TIMEOUT)
		if raw is None:
			return None
		return DeploymentResponse.model_validate_json(raw).result

	def waypoints(self) -> Optional[WaypointInfo]:
		# Legacy code hits /api/wp.  The OpenAPI spec only documents
		# /api/vehicles/waypoints; both currently respond identically on
		# okeanids, but /api/wp is what production has hit for years.
		query = urllib.parse.urlencode({"vehicle": self.vehicle})
		raw = self._get(self._url("wp", query), timeout=NEWSTYLE_TIMEOUT)
		if raw is None:
			return None
		return WpInfoResponse.model_validate_json(raw).result

	def script_description(self, script_path: str) -> Optional[WpMissionDescription]:
		query = urllib.parse.urlencode({"vehicle": self.vehicle, "path": script_path})
		raw = self._get(
			self._url("commands/script", query), timeout=NEWSTYLE_TIMEOUT
		)
		if raw is None:
			return None
		return ScriptDescriptionResponse.model_validate_json(raw).result

	def mission_xml(self, mission: str) -> Optional[object]:
		"""Fetch /api/git/mission/{mission}.xml; return the parsed `result` field."""
		raw = self._get(
			self._url(f"git/mission/{mission}.xml"), timeout=NEWSTYLE_TIMEOUT
		)
		if raw is None:
			return None
		return json.loads(raw).get("result")

	def shore_asc(self, sbdlog_path: str) -> Optional[str]:
		"""Fetch /TethysDash/data/<vehicle>/realtime/sbdlogs/<path>/shore.asc as text.

		Note: this lives under /TethysDash/data/, not /TethysDash/api/, and
		returns plain ASCII (the on-vehicle SBD log dump), not JSON.
		"""
		url = (
			f"{self._scheme}://{self.server}/TethysDash/data/"
			f"{self.vehicle}/realtime/sbdlogs/{sbdlog_path}/shore.asc"
		)
		raw = self._get(url, timeout=NEWSTYLE_TIMEOUT)
		if raw is None:
			return None
		return raw.decode("utf-8")

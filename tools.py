import hashlib
import re
from difflib import SequenceMatcher
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from crewai_tools import YoutubeChannelSearchTool
from crewai_tools.rag.data_types import DataType
from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.tools.youtube_channel_search_tool.youtube_channel_search_tool import (
	FixedYoutubeChannelSearchToolSchema,
)


class VideoTranscriptSearchTool(YoutubeChannelSearchTool):
	def add_video(self, video_url: str) -> None:
		RagTool.add(self, video_url, data_type=DataType.YOUTUBE_VIDEO)


def normalize_channel_url(channel: str) -> str:
	value = channel.strip()
	if not value:
		raise ValueError("Enter a YouTube channel handle or URL.")
	if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", value):
		return f"https://www.youtube.com/channel/{value}"
	if not value.startswith(("http://", "https://")):
		handle = value if value.startswith("@") else f"@{value}"
		if not re.fullmatch(r"@[A-Za-z0-9._-]+", handle):
			raise ValueError("Enter a valid YouTube channel handle.")
		value = f"https://www.youtube.com/{handle}"

	parsed = urlparse(value)
	host = parsed.netloc.lower().removeprefix("www.")
	if host not in {"youtube.com", "m.youtube.com"}:
		raise ValueError("Enter a YouTube channel URL, not a video URL.")
	if re.fullmatch(r"/channel/UC[A-Za-z0-9_-]{22}", parsed.path):
		return f"https://www.youtube.com{parsed.path}"
	if parsed.path.startswith("/@"):
		return f"https://www.youtube.com{parsed.path.rstrip('/')}"
	raise ValueError("Use a YouTube channel ID or @handle URL.")


def _resolve_channel_id(channel_url: str) -> str:
	match = re.search(r"/channel/(UC[A-Za-z0-9_-]{22})", channel_url)
	if match:
		return match.group(1)

	request = Request(channel_url, headers={"User-Agent": "Mozilla/5.0"})
	try:
		with urlopen(request, timeout=15) as response:
			html = response.read(2_000_000).decode("utf-8", errors="ignore")
	except URLError as error:
		raise ValueError(f"Could not open YouTube channel URL: {error}") from error
	match = re.search(r'"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"', html)
	if not match:
		raise ValueError(f"Could not resolve YouTube channel ID: {channel_url}")
	return match.group(1)


def _fetch_channel_videos(channel_url: str) -> list[tuple[str, str]]:
	channel_id = _resolve_channel_id(channel_url)
	feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
	request = Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
	try:
		with urlopen(request, timeout=20) as response:
			feed = ElementTree.fromstring(response.read())
	except (URLError, ElementTree.ParseError) as error:
		raise ValueError(f"Could not load the channel's public video feed: {error}") from error

	atom = "{http://www.w3.org/2005/Atom}"
	media = "{http://www.youtube.com/xml/schemas/2015}"
	videos = []
	for entry in feed.findall(f"{atom}entry"):
		title = entry.findtext(f"{atom}title", default="").strip()
		video_id = entry.findtext(f"{media}videoId", default="").strip()
		if title and video_id:
			videos.append((title, f"https://www.youtube.com/watch?v={video_id}"))
	return videos


def _normalize_title(value: str) -> str:
	return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _select_channel_videos(videos: list[tuple[str, str]], topic: str) -> list[str]:
	target = _normalize_title(topic)
	if not target:
		return []

	target_words = set(target.split())
	scored = []
	for title, url in videos:
		normalized = _normalize_title(title)
		overlap = len(target_words & set(normalized.split())) / len(target_words)
		score = max(overlap, SequenceMatcher(None, target, normalized).ratio())
		scored.append((score, url))

	scored.sort(reverse=True)
	if not scored or scored[0][0] < 0.45:
		return []
	if scored[0][0] >= 0.8:
		return [scored[0][1]]
	return [url for score, url in scored[:3] if score >= 0.35]


def _normalize_video_url(video_url: str) -> str:
	parsed = urlparse(video_url.strip())
	host = parsed.netloc.lower().removeprefix("www.")
	if host == "youtu.be":
		video_id = parsed.path.strip("/").split("/", 1)[0]
	elif host in {"youtube.com", "m.youtube.com"}:
		if parsed.path == "/watch":
			video_id = parse_qs(parsed.query).get("v", [""])[0]
		else:
			match = re.fullmatch(r"/(?:shorts|embed|v)/([A-Za-z0-9_-]{11})", parsed.path)
			video_id = match.group(1) if match else ""
	else:
		video_id = ""
	if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
		raise ValueError("Enter a valid YouTube video URL.")
	return f"https://www.youtube.com/watch?v={video_id}"


def create_channel_tool(channel: str, topic: str, video_url: str = "") -> VideoTranscriptSearchTool:
	if video_url.strip():
		video_urls = [_normalize_video_url(video_url)]
	else:
		channel_url = normalize_channel_url(channel)
		videos = _fetch_channel_videos(channel_url)
		video_urls = _select_channel_videos(videos, topic)
		if not video_urls:
			raise ValueError(
				"No matching video was found in the channel's recent public feed. "
				"Provide the direct YouTube video URL to retrieve its transcript."
			)

	source_key = "|".join(sorted(video_urls))
	collection_name = f"youtube_videos_{hashlib.sha256(source_key.encode()).hexdigest()[:16]}"
	tool = VideoTranscriptSearchTool(
		collection_name=collection_name,
		config={"embedding_model": {"provider": "onnx"}},
	)
	tool.args_schema = FixedYoutubeChannelSearchToolSchema
	tool.description = "Search the transcript of the selected YouTube lecture video or videos."
	for video in video_urls:
		tool.add_video(video)
	return tool

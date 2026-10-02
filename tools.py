import hashlib
import re
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from crewai_tools import YoutubeChannelSearchTool
from crewai_tools.rag.data_types import DataType
from crewai_tools.tools.rag.rag_tool import RagTool


class ChannelSearchTool(YoutubeChannelSearchTool):
	def add(self, youtube_channel_handle: str) -> None:
		RagTool.add(
			self,
			normalize_channel_url(youtube_channel_handle),
			data_type=DataType.YOUTUBE_CHANNEL,
		)


def normalize_channel_url(channel: str) -> str:
	value = channel.strip()
	if not value:
		raise ValueError("Enter a YouTube channel handle or URL.")

	if value.startswith(("https://", "http://")):
		parsed = urlparse(value)
		host = parsed.netloc.lower().removeprefix("www.")
		if host not in {"youtube.com", "m.youtube.com"}:
			raise ValueError("Enter a youtube.com channel URL or an @handle.")
		path = parsed.path.rstrip("/")
		if path.startswith("/@"):
			return _resolve_handle(f"https://www.youtube.com{path}")
		if re.fullmatch(r"/channel/UC[A-Za-z0-9_-]{22}", path):
			return f"https://www.youtube.com{path}"
		if re.fullmatch(r"/(?:c|user)/[A-Za-z0-9._%-]+", path):
			return f"https://www.youtube.com{path}"
		raise ValueError("Use a YouTube channel URL, not a video URL.")

	if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", value):
		return f"https://www.youtube.com/channel/{value}"

	handle = value if value.startswith("@") else f"@{value}"
	if not re.fullmatch(r"@[A-Za-z0-9._-]+", handle):
		raise ValueError("Enter a channel @handle or a supported YouTube channel URL.")
	return _resolve_handle(f"https://www.youtube.com/{handle}")


def _resolve_handle(handle_url: str) -> str:
	request = Request(handle_url, headers={"User-Agent": "Mozilla/5.0"})
	try:
		with urlopen(request, timeout=15) as response:
			html = response.read(2_000_000).decode("utf-8", errors="ignore")
	except URLError as error:
		raise ValueError(f"Could not open YouTube channel URL: {error}") from error

	for pattern in (
		r'"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
		r'"channelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
	):
		match = re.search(pattern, html)
		if match:
			return f"https://www.youtube.com/channel/{match.group(1)}"
	raise ValueError(f"Could not resolve YouTube channel handle: {handle_url}")


def create_channel_tool(channel: str) -> ChannelSearchTool:
	channel_url = normalize_channel_url(channel)
	collection_hash = hashlib.sha256(channel_url.encode("utf-8")).hexdigest()[:16]
	return ChannelSearchTool(
		youtube_channel_handle=channel_url,
		collection_name=f"youtube_channel_{collection_hash}",
		config={"embedding_model": {"provider": "onnx"}},
	)

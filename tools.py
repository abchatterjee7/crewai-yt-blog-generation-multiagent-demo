from crewai_tools import YoutubeChannelSearchTool
from crewai_tools.rag.data_types import DataType
from crewai_tools.tools.rag.rag_tool import RagTool

class ChannelSearchTool(YoutubeChannelSearchTool):
	def add(self, youtube_channel_handle: str) -> None:
		channel_url = (
			youtube_channel_handle
			if youtube_channel_handle.startswith("http")
			else f"https://www.youtube.com/{youtube_channel_handle}"
		)
		RagTool.add(self, channel_url, data_type=DataType.YOUTUBE_CHANNEL)

# Use Chroma's local ONNX embedder so search does not require an OpenAI API key.
yt_tool = ChannelSearchTool(
	youtube_channel_handle='https://www.youtube.com/channel/UCjYznQJKcb-jToT4nj54RGA',
	config={
		"embedding_model": {
			"provider": "onnx",
		}
	},
)
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import openai


def get_video_id(video_url):
    """
    Retrieves the video ID using pytube.
    """
    try:
        # Create a YouTube object
        yt = YouTube(video_url)
        return yt.video_id
    except Exception as e:
        raise ValueError(f"Failed to retrieve video ID: {e}")


def fetch_transcript_with_timestamps(video_url):
    """
    Fetches subtitles with timestamps from a YouTube video, including auto-generated ones.
    :param video_url: URL of the YouTube video
    :return: List of subtitles with timestamps or an error message
    """
    try:
        # Get the video ID using pytube
        video_id = get_video_id(video_url)

        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'a.en'])

        # Format the transcript with timestamps
        formatted_transcript = []
        for entry in transcript:
            start_time = entry['start']  # Start time of the subtitle (in seconds)
            duration = entry['duration']  # Duration of the subtitle (in seconds)
            text = entry['text']  # The subtitle text
            formatted_transcript.append({
                "start_time": start_time,
                "end_time": start_time + duration,
                "text": text
            })

        return formatted_transcript
    except Exception as e:
        return f"Error: {e}"


def format_timestamp(seconds):
    """
    Converts seconds into a human-readable timestamp (hh:mm:ss).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def summarize_with_chatgpt(transcript, openai_api_key, model="gpt-3.5-turbo"):
    """
    Summarizes the transcript using ChatGPT while preserving timestamps.
    :param transcript: List of dictionaries with "start_time", "end_time", and "text".
    :param openai_api_key: OpenAI API key for authentication.
    :param model: The model to use (default: gpt-3.5-turbo).
    :return: List of summarized events with timestamps or an error message.
    """
    try:
        # Combine the subtitles into a single formatted string
        subtitles = "\n".join(
            f"[{format_timestamp(entry['start_time'])} - {format_timestamp(entry['end_time'])}] {entry['text']}"
            for entry in transcript
        )

        # Define the prompt for ChatGPT
        prompt = (
            "You are a professional summarizer for YouTube videos. Below are subtitles with timestamps from a video. "
            "Summarize the key events while preserving the timestamps for each summarized point.\n\n"
            f"Subtitles:\n{subtitles}\n\n"
            "Summarize this information into a concise list of key events with timestamps."
        )

        # Call the ChatGPT API
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You summarize YouTube subtitles with timestamps."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summarized content
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during summarization: {e}"


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")  # Input the video URL
    openai_api_key = input("Enter your OpenAI API key: ")  # Input OpenAI API key

    transcript = fetch_transcript_with_timestamps(video_url)

    if isinstance(transcript, str):  # If there was an error, it's returned as a string
        print(transcript)
    else:
        print("\nSubtitles with Timestamps:")
        for entry in transcript:
            start_time = format_timestamp(entry["start_time"])
            end_time = format_timestamp(entry["end_time"])
            text = entry["text"]
            print(f"[{start_time} - {end_time}] {text}")

        # Generate summary with ChatGPT
        print("\nSummary with Timestamps:")
        summary = summarize_with_chatgpt(transcript, openai_api_key)
        print(summary)

from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import openai


def get_video_id(video_url):
    """
    Retrieves the video ID using pytube.
    """
    try:
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

        # Fetch the transcript (tries human-made first, then auto-generated 'a.en')
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'a.en'])

        # Format the transcript with timestamps
        formatted_transcript = []
        for entry in transcript:
            start_time = entry['start']          # start time (seconds)
            duration = entry['duration']         # duration (seconds)
            text = entry['text']                 # caption text
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
    (Original single-shot summarizer — kept intact)
    Summarizes the transcript using ChatGPT while preserving timestamps.
    :param transcript: List of dicts with "start_time", "end_time", and "text".
    :param openai_api_key: OpenAI API key.
    :param model: Chat model (default: gpt-3.5-turbo).
    :return: Summarized text or an error message.
    """
    try:
        # Combine subtitles into a single formatted string
        subtitles = "\n".join(
            f"[{format_timestamp(entry['start_time'])} - {format_timestamp(entry['end_time'])}] {entry['text']}"
            for entry in transcript
        )

        # Define prompt
        prompt = (
            "You are a professional summarizer for YouTube videos. Below are subtitles with timestamps from a video. "
            "Summarize the key events while preserving the timestamps for each summarized point.\n\n"
            f"Subtitles:\n{subtitles}\n\n"
            "Summarize this information into a concise list of key events with timestamps."
        )

        # Call ChatGPT
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You summarize YouTube subtitles with timestamps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error during summarization: {e}"

def chunk_text_by_chars(text: str, max_chars: int = 6000):
    if len(text) <= max_chars:
        return [text]
    chunks, cur, cur_len = [], [], 0
    for line in text.splitlines():
        L = len(line) + 1
        if cur_len + L > max_chars and cur:
            chunks.append("\n".join(cur))
            cur, cur_len = [], 0
        cur.append(line)
        cur_len += L
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def summarize_chunk_with_chatgpt(subtitles_chunk: str, openai_api_key: str, model: str):
    openai.api_key = openai_api_key

    system_msg = "You summarize YouTube subtitles with timestamps."
    user_prompt = (
        "You are a professional summarizer for YouTube videos. Below is a chunk of subtitles with timestamps. "
        "Summarize the key points for this chunk while preserving the timestamps you see.\n\n"
        f"{subtitles_chunk}\n\n"
        "Output 5–10 concise bullet points, retaining timestamps where present."
    )

    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def summarize_with_chatgpt_chunked(transcript, openai_api_key, model="gpt-3.5-turbo", max_chars=7000):
    try:
        # 1) Format subtitles (timestamped)
        formatted = "\n".join(
            f"[{format_timestamp(e['start_time'])} - {format_timestamp(e['end_time'])}] {e['text']}"
            for e in transcript
        )

        # 2) Chunk by size
        chunks = chunk_text_by_chars(formatted, max_chars=max_chars)

        # 3) Map: summarize each chunk
        partial_summaries = [
            summarize_chunk_with_chatgpt(ch, openai_api_key=openai_api_key, model=model)
            for ch in chunks
        ]

        # 4) Reduce: merge partials into a single concise outline
        openai.api_key = openai_api_key
        system_msg = "You merge multiple partial summaries into one coherent outline, keeping useful timestamps."
        user_prompt = (
            "Merge the following partial summaries into one concise list of key events (10–15 bullets). "
            "If multiple timestamps refer to the same idea, keep the earliest. Keep timestamps where present.\n\n"
            + "\n\n---\n\n".join(partial_summaries)
        )

        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during summarization (chunked): {e}"


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")      # Input the video URL
    openai_api_key = input("Enter your OpenAI API key: ")   # Input OpenAI API key

    transcript = fetch_transcript_with_timestamps(video_url)

    if isinstance(transcript, str): 
        print(transcript)
    else:
        print("\nSubtitles with Timestamps:")
        for entry in transcript:
            start_time = format_timestamp(entry["start_time"])
            end_time = format_timestamp(entry["end_time"])
            text = entry["text"]
            print(f"[{start_time} - {end_time}] {text}")

        print("\nSummary with Timestamps:")
        summary = summarize_with_chatgpt_chunked(
            transcript,
            openai_api_key,
            model="gpt-3.5-turbo",
            max_chars=6000
        )
        print(summary)

from datetime import datetime
import re

def get_subtitle_file_bookend_timestamps(filepath: str) -> tuple[int,int]:
    """For displaying slider for user to select part of SRT file they want to add to a subtitle file

    Args:
        filepath (str): path to uploaded SRT tile

    Returns:
        tuple[int,int]: begin, end in seconds, e.g. (5, 2500) = from 0:00:05 to 0:41:40
    """
    # with open(filepath, 'r', encoding='UTF-8') as f:
    #     subtitle_file_contents = f.read().decode('utf-8')

    subtitle_file_contents = filepath.read().decode('utf-8')
    subtitles_dict = get_times_and_subtitles_dict(subtitle_file_contents)
    first_timestamp = list(subtitles_dict.keys())[0]
    last_timestamp = list(subtitles_dict.keys())[-1]
    return (first_timestamp, last_timestamp)

def get_subtitle_contents_from_srt(filepath: str, timestamps: tuple[int, int]=(0,0)) -> str:
    """Entry-point function for extracting subtitles from an SRT file

    Args:
        filepath (str): _description_
        timestamps (tuple[int, int]): beginning and ending of relevant section of subtitles in seconds, e.g. 2:30:15 to 2:31:15 is (9015,9075). Default is (0,0), at which point all subtitles will be returned
    Returns:
        str: formatted string that is ready to be saved as a subtitle csv, with individual subtitles separated by line break
    """
    with open(filepath, 'r', encoding='UTF-8') as f:
        subtitle_file_contents = f.read()
    
    subtitles_dict = get_times_and_subtitles_dict(subtitle_file_contents)
    filtered_subtitles = filter_subtitles_based_on_timestamp(subtitles_dict, timestamps)
    return filtered_subtitles

def filter_subtitles_based_on_timestamp(subtitles_dict: dict[int, str], timestamps: tuple[int,int]) -> str:
    """Takes subtitle_dict output from get_times_and_subtitles_dict and removes all contents not in the period defined by timestamps

    Args:
        subtitles_dict (dict): keys are timestamps in seconds, values are subtitles
        timestamps (tuple[int, int]): beginning and ending of relevant section of subtitles in seconds, e.g. 2:30:15 to 2:31:15 is (9015,9075). Default is (0,0), at which point all subtitles will be returned

    Returns:
        str: filtered, line break-separated subtitles
    """
    if timestamps == (0,0): # in case no timestamps are passed, returned all subtitles
        return '\n'.join(list(subtitles_dict.values()))
    start = timestamps[0]
    end = timestamps[1]
    subtitle_timestamps = list(subtitles_dict.keys())
    filtered_timestamps = [subtitle for subtitle in subtitle_timestamps if subtitle > start and subtitle < end]
    filtered_subtitles = []
    for t in filtered_timestamps:
        filtered_subtitles.append(subtitles_dict[t])

    return '\n'.join(filtered_subtitles)

def get_times_and_subtitles_dict(subtitle_file_contents: str) -> dict[str:str]:
    """Takes in string SRT file contents and outputs a dict containing {timestamp: subtitle}

    Args:
        subtitle_file_contents (str): Raw SRT file contents
    Returns:
        dict: {timestamps:subtitles}
    """
    subtitle_file_split = subtitle_file_contents.split('\r\n\r\n') # artifact of decoding json from '\n\n' in srt
    times = []
    subtitles = []
    for subtitle_contents in subtitle_file_split:
        contents = subtitle_contents.split('\n')
        time = format_timestamp(re.match(pattern=r'(.*) -->', string=contents[1]).groups()[0])
        times.append(time)
        subtitles.append(contents[2])
    subtitles_dict = dict(zip(times, subtitles))

    return subtitles_dict

def format_timestamp(timestamp: str) -> int:
    """takes in a timestamp in the .SRT standard and outputs a datetime object

    Args:
        timestamp (str): .SRT timestamp, e.g. '00:02:12,132'

    Returns:
        int: second that the timestamp occurred, e.g. 1hr, 20 min, 10 seconds = 4810 seconds
    """
    time_format = '%H:%M:%S,%f'
    _datetime = datetime.strptime(timestamp, time_format) 
    seconds = (_datetime.hour * 3600) + (_datetime.minute * 60) + _datetime.second
    return seconds

if __name__ == "__main__":
    filepath = './data/subtitles/uploaded_subtitles/To_Live.srt'
    get_subtitle_file_bookend_timestamps(filepath)
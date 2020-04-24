import urllib.request
import json
import datetime
import os, argparse


def get_single_track_data_from_drf(track):

    # Form URL
    race_url = f'https://www.drf.com/liveOdds/tracksPoolDetails/currentRace/{track["currentRace"]}/' \
               f'trackId/{track["trackId"]}/' \
               f'country/{track["country"]}/' \
               f'dayEvening/{track["dayEvening"]}/' \
               f'date/{datetime.datetime.now().strftime("%m-%d-%Y")}'

    # Get Data
    with urllib.request.urlopen(race_url) as url:
        data = json.loads(url.read().decode())

    data['drf_scrape'] = {
        'time_scrape_utc': datetime.datetime.utcnow().isoformat()
    }

    # Return
    return data


def get_track_list(request_date):

    # Get current track list
    drf_format_date = request_date.strftime("%m-%d-%Y")
    drf_track_url = "http://www.drf.com/liveOdds/getTrackList/date/" + drf_format_date
    with urllib.request.urlopen(drf_track_url) as url:
        track_data = json.loads(url.read().decode())

    # Return track list
    return track_data


def save_single_track_data_to_file(data, save_dir):

    # Get necessary data

    race_scraped_datetime = datetime.datetime.fromisoformat(data['drf_scrape']['time_scrape_utc'])
    if int(data['raceKey']['raceDate']['date']) > 0:
        race_datetime = datetime.datetime(
            day=data['raceKey']['raceDate']['day'],
            month=data['raceKey']['raceDate']['month'] + 1,
            year=data['raceKey']['raceDate']['year']
        )
    else:
        print('date is negative!')
        race_datetime = datetime.datetime.fromisoformat(data['drf_scrape']['time_scrape_utc'])
    track_id = data['raceKey']['trackId']

    # Assemble path
    data_path = os.path.join(save_dir, track_id, str(race_datetime.year), str(race_datetime.month))
    data_filepath = os.path.join(
        data_path,
        f'{track_id}_'
        f'{race_datetime.year:04.0f}{race_datetime.month:02.0f}{race_datetime.day:02.0f}_'
        f'{data["raceKey"]["raceNumber"]}_'
        f'{race_scraped_datetime.year:04.0f}{race_scraped_datetime.month:02.0f}{race_scraped_datetime.day:02.0f}T'
        f'{race_scraped_datetime.hour:02.0f}{race_scraped_datetime.minute:02.0f}{race_scraped_datetime.second:02.0f}_'
        f'odds.json'
    )

    # Verify Folder Exists
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Write File
    with open(data_filepath, 'w') as outfile:
        json.dump(data, outfile)


def get_current_track_list():

    # Wrapper for the current time
    return get_track_list(datetime.datetime.now())


if __name__ == '__main__':

    # Argument Parsing
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--mode',
                            help="Mode of operation (odds: store odds files)",
                            type=str,
                            required=True,
                            metavar='MODE'
                            )
    arg_parser.add_argument('--output_dir',
                            help="Base directory for storing json files",
                            type=str,
                            metavar='PATH'
                            )
    args = arg_parser.parse_args()

    # Check mode
    if args.mode == 'odds':

        # Just store odds files
        print('Running in odds collection mode')

        # Check output directory
        base_data_dir = args.output_dir.strip()
        if base_data_dir == '' or not os.path.exists(base_data_dir):
            print(f'The output directory of "{base_data_dir}" is invalid!')
            exit(1)

        # Get currently running tracks
        track_data = get_current_track_list()

        # Iterate through tracks
        for current_track in track_data:
            race_data = get_single_track_data_from_drf(current_track)
            print(race_data)
            save_single_track_data_to_file(race_data, base_data_dir)

    else:
        print(f'"{args.mode}" is not a valid operational mode!')
        exit(1)

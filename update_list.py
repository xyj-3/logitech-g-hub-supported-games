"""For use with the update-g-hub-list workflow. Uses a file ghub_version.txt in the repository and runs on Windows
with LGHUB installed at the default location."""

import json
import re
from datetime import datetime


def main():
    # get the G HUB version number of the repository
    repo_version_file = "ghub_version.txt"
    try:
        with open(repo_version_file) as f:
            version_repo = f.read().strip()
    except FileNotFoundError:
        raise Exception("ghub_version.txt not found")

    # get the latest G HUB version number
    version_file = "C:/ProgramData/LGHUB/current.json"
    try:
        with open(version_file) as f:
            version_data = json.load(f)
        version = version_data["version"]
        version_shortened = re.sub(r"^(\d{4}\.\d+)\.\d+$", r"\1", version)
        build_id = version_data["buildId"]
    except FileNotFoundError:
        raise Exception("current.json not found")

    if version != version_repo:  # update g-hub-games-list.md
        # Get the release date
        release_date_file_path = f"C:/ProgramData/LGHUB/depots/{build_id}/release_notes/notes/index.html"
        try:
            with open(release_date_file_path) as f:
                release_date_file = f.read()
            release_date_pre = re.search(r"Released on ([A-Za-z]+ \d{1,2}, \d{4})\.", release_date_file).group(1)
            # Try both full month name (%B) and abbreviated month name (%b)
            try:
                date_obj = datetime.strptime(release_date_pre, "%B %d, %Y")
            except ValueError:
                date_obj = datetime.strptime(release_date_pre, "%b %d, %Y")
            release_date = date_obj.strftime("%Y/%m/%d")
        except FileNotFoundError:
            raise Exception("release_notes.html not found")

        # Create the new version of the list
        data_file_path = "C:/Program Files/LGHUB/data/applications.json"
        try:
            with open(data_file_path) as f1:
                data = json.load(f1)

            with open("g-hub-games-list.md", "w+", encoding="utf-8") as f2:
                game_count = 0
                games_string = ""

                f2.write("# Logitech G HUB supported games list\n\n")
                f2.write(
                    f"This is a list of games supported by Logitech G HUB software. It is accurate as of G HUB version {version_shortened}, released on {release_date}.\n\n")

                for application in data["applications"]:
                    games_string += "> " + (application["name"]) + "  \n"
                    game_count += 1

                f2.write(f"There are {game_count} games on this list.\n\n")
                f2.write(games_string)
        except FileNotFoundError:
            raise Exception("applications.json not found")

        # Update version.txt
        with open(repo_version_file, "w") as f:
            f.write(version)

        # print out version for the commit message
        print(version_shortened)


if __name__ == "__main__":
    main()

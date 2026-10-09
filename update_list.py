"""For use with the update-g-hub-list workflow. Uses a file ghub_version.txt in the repository and runs on Windows
with LGHUB installed at the default location."""

import json
import re
from datetime import datetime

# The games list is also embedded in README.md between these two markers
README_START_MARKER = "<!-- GAMES-LIST:START -->"
README_END_MARKER = "<!-- GAMES-LIST:END -->"


def embed_list_in_readme(readme, list_body):
    """Return the README text with everything between the markers replaced by list_body."""
    start = readme.find(README_START_MARKER)
    end = readme.find(README_END_MARKER, start + 1)
    if start == -1 or end == -1:
        raise Exception(f"{README_START_MARKER} and {README_END_MARKER} markers not found in README.md")
    start += len(README_START_MARKER)
    return readme[:start] + "\n\n" + list_body + "\n" + readme[end:]


def main():
    # get the G HUB version number of the repository
    repo_version_file = "ghub_version.txt"
    try:
        with open(repo_version_file, encoding="utf-8") as f:
            version_repo = f.read().strip()
    except FileNotFoundError:
        raise Exception("ghub_version.txt not found")

    # get the latest G HUB version number
    version_file = "C:/ProgramData/LGHUB/current.json"
    try:
        with open(version_file, encoding="utf-8") as f:
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
            # Explicit encoding: the Windows default (cp1252) can't decode the UTF-8 characters in the release notes
            with open(release_date_file_path, encoding="utf-8") as f:
                release_date_file = f.read()
            release_date_match = re.search(r"Released on ([A-Za-z]+ \d{1,2}, \d{4})\.", release_date_file)
            if release_date_match is None:
                raise Exception("release date not found in release notes")
            release_date_pre = release_date_match.group(1)
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
            with open(data_file_path, encoding="utf-8") as f1:
                data = json.load(f1)
        except FileNotFoundError:
            raise Exception("applications.json not found")

        game_count = 0
        games_string = ""
        for application in data["applications"]:
            games_string += "> " + (application["name"]) + "  \n"
            game_count += 1

        # Everything below the title: shared by g-hub-games-list.md and the README
        list_body = (
            f"This is a list of games supported by Logitech G HUB software. It is accurate as of G HUB version {version_shortened}, released on {release_date}.\n\n"
            f"There are {game_count} games on this list.\n\n"
            f"{games_string}"
        )

        # Build the new README before writing anything, so a missing marker can't leave the files out of sync
        try:
            with open("README.md", encoding="utf-8") as f3:
                readme = f3.read()
        except FileNotFoundError:
            raise Exception("README.md not found")
        new_readme = embed_list_in_readme(readme, list_body)

        with open("g-hub-games-list.md", "w+", encoding="utf-8") as f2:
            f2.write("# Logitech G HUB supported games list\n\n")
            f2.write(list_body)

        with open("README.md", "w", encoding="utf-8") as f3:
            f3.write(new_readme)

        # Update version.txt
        with open(repo_version_file, "w", encoding="utf-8") as f:
            f.write(version)

        # print out version for the commit message
        print(version_shortened)


if __name__ == "__main__":
    main()

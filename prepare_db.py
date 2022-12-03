#!/usr/bin/python -u

from csv import DictReader
from json import load
from pathlib import Path
from string import punctuation
from sys import stdout
from zipfile import ZipFile

from shapely.geometry import MultiPolygon, shape
from sqlite_utils import Database
from unidecode import unidecode
from xlrd import open_workbook


translation_table = str.maketrans("", "", punctuation)


def clean_name(name):
    return unidecode(name).translate(translation_table)


def find_matching_candidate(candidates, name):
    # if we have an exact match, return it
    for candidate in candidates:
        if clean_name(candidate["name"]) == name:
            return candidate

    cleaned_name = clean_name(name)

    # otherwise, let's hunt for a match
    # modified_name = name.replace(" JR", "").strip()
    last_name = cleaned_name.split()[-1]

    # if we have a match on last name, return it
    possible_matches = [c for c in candidates if last_name in clean_name(c["name"])]

    # if we have a single match, return it
    if len(possible_matches) == 1:
        return possible_matches[0]

    # one last try, let's try to match on first name
    first_name = cleaned_name.split()[0]

    # if we have a match on first name, return it
    possible_matches = [c for c in candidates if first_name in clean_name(c["name"])]

    # if we have a single match, return it
    if len(possible_matches) == 1:
        return possible_matches[0]

    # ugh let's try to remove a prefix
    last_name_without_prefix = cleaned_name.replace("JR", "").strip().split()[-1]

    # if we have a match on last name, return it
    possible_matches = [
        c for c in candidates if last_name_without_prefix in clean_name(c["name"])
    ]

    # if we have a single match, return it
    if len(possible_matches) == 1:
        return possible_matches[0]

    raise ValueError(f"Could not find a match for {name}")


def run():
    # Create a ZipFile object from the response and extract
    with ZipFile("inputs/statement_of_votes_cast.zip") as zipfile:
        zipfile.extractall("tmp/results/")

    # Create a database
    db = Database("tmp/results.db", recreate=True)

    # Bootstrap the precincts table
    with open("inputs/precincts.csv") as infile:
        reader = DictReader(infile)

        for row in reader:
            # Load each of our precincts
            db["precincts"].insert(
                {
                    "precinct": row["Precinct"],
                    "ballot_group": row["BallotGroup"],
                    "serial_number": row["SerialNumber"],
                },
                pk="precinct",
                columns={"ballot_group": int, "serial_number": int},
            )

    # Bootstrap the contests table
    with open("inputs/election_data.json") as infile:
        data = load(infile)

        contest_groups = data["Data"]["ContestGroups"]

        for contest_group in contest_groups:
            group = contest_group["Name"]
            contests = contest_group["Contests"]

            for contest in contests:
                contest_id = contest["ID"]

                db["contests"].insert(
                    {
                        "id": contest_id,
                        "group": group,
                        "name": contest["Title"],
                        "type": contest["Type"],
                    },
                    pk="id",
                )

                candidates = contest["Candidates"]

                for candidate in candidates:
                    db["candidates"].insert(
                        {
                            "id": candidate["ID"],
                            "name": candidate["Name"],
                            "party": candidate["Party"],
                            "contest_id": contest_id,
                        },
                        pk="id",
                        foreign_keys=[("contest_id", "contests", "id")],
                    )

    # Find all the Excel files in the results directory
    files = Path("tmp/results/").glob("*.xls")

    # Loop through each file
    stdout.write("Loading results\n")

    for file in files:
        stdout.write(".")
        stdout.flush()

        # Grab the contest ID from the filename
        contest_id = int(file.stem.split("-")[-1])

        # Open the Excel file
        workbook = open_workbook(file)

        # Grab the first (and only) sheet
        sheet = workbook.sheet_by_index(0)

        # Grab the column names from the header row (row 2)
        headers = sheet.row_values(2)
        candidate_names = [s for s in headers[8:] if s]

        results = []

        # Loop through the remaining rows
        for index in range(3, sheet.nrows):
            # Grab the values for this row
            values = sheet.row_values(index)

            # Create a dictionary of {column_name: value}
            row_data = dict(zip(headers, values))

            precinct_id = row_data["PRECINCT"]
            type = row_data["TYPE"]
            candidates = list(
                db["candidates"].rows_where("contest_id = ?", [contest_id])
            )

            for name in candidate_names:
                candidate = find_matching_candidate(candidates, name)

                results.append(
                    {
                        "candidate_id": candidate["id"],
                        "contest_id": contest_id,
                        "precinct_id": precinct_id,
                        "type": type,
                        "votes": row_data[name],
                    }
                )

        db["results"].insert_all(
            results,
            columns={"votes": int},
            foreign_keys=[
                ("candidate_id", "candidates", "id"),
                ("contest_id", "contests", "id"),
                ("precinct_id", "precincts", "precinct"),
            ],
            batch_size=1_000,
        )

    # Initialize SpatiaLite
    db.init_spatialite()

    # Add a SpatiaLite 'geometry' column
    db["precincts"].add_geometry_column("geometry", "MULTIPOLYGON")

    with open("inputs/precincts.json") as infile:
        collection = load(infile)

        stdout.write("\nLoading precinct geographies\n")

        for feature in collection["features"]:
            stdout.write(".")
            stdout.flush()

            precinct_id = feature["properties"]["Precinct"]
            geometry = shape(feature["geometry"])

            # We need to convert the geometry to a MultiPolygon
            if geometry.type == "Polygon":
                geometry = MultiPolygon([geometry])

            db["precincts"].update(
                precinct_id,
                {"geometry": geometry.wkt},
                conversions={"geometry": "GeomFromText(?, 4326)"},
            )


if __name__ == "__main__":
    run()

from itertools import groupby
from json import dumps

from sqlite_utils import Database


def prepare_candidate(candidate):
    return {
        "id": candidate["id"],
        "name": candidate["name"],
        "party": candidate["party"],
        "votes": candidate["total_votes"],
    }


def prepare_contest(db, contest):
    id = contest["id"]

    # Find all the candidates participating in this contest
    candidates = [
        prepare_candidate(candidate)
        for candidate in db["candidates"].rows_where(
            "contest_id = ?", [id], "total_votes DESC"
        )
    ]

    results = db.query(
        """
        SELECT
            results.precinct_id,
            candidates.id,
            candidates.name,
            results.polling_place,
            results.vote_by_mail,
            results.total
        FROM results
        JOIN candidates ON candidates.id = results.candidate_id
        WHERE results.contest_id = ?
        ORDER BY results.precinct_id, results.total DESC
        """,
        [id],
    )

    # Group the results by precinct
    grouped = groupby(results, lambda r: r["precinct_id"])

    precincts = []

    for precinct, cands in grouped:
        precincts.append(
            {
                "precinct": precinct,
                "candidates": [
                    {
                        "id": cand["id"],
                        "name": cand["name"],
                        "polling_place": cand["polling_place"],
                        "vote_by_mail": cand["vote_by_mail"],
                        "total": cand["total"],
                    }
                    for cand in cands
                ],
            }
        )

    return {
        "id": id,
        "name": contest["name"],
        "group": contest["group"],
        "type": contest["type"],
        "non_partisan": contest["non_partisan"] == 1,
        "voter_nominated": contest["voter_nominated"] == 1,
        "vote_for": contest["vote_for"],
        "candidates": candidates,
        "precincts": precincts,
    }


def run():
    db = Database("tmp/results.db")

    # results = [prepare_contest(db, contest) for contest in db["contests"].rows]
    results = [prepare_contest(db, contest) for contest in db["contests"].rows]

    with open("tmp/precinct_results.json", "w") as outfile:
        outfile.write(dumps(results, indent=2))


if __name__ == "__main__":
    run()

from csv import DictWriter

from sqlite_utils import Database


def generate_contest_results_csv(db):
    rows = db.query(
        """
        SELECT
        contests.id as contest_id,
        contests.name as contest,
        contests.[group] as contest_group,
        contests.type as contest_type,
        contests.non_partisan,
        contests.voter_nominated,
        contests.vote_for,
        candidates.id as candidate_id,
        candidates.name,
        candidates.party,
        candidates.total_votes
        FROM
        candidates
        JOIN contests ON candidates.contest_id = contests.id
        ORDER BY
        contests.id, candidates.total_votes DESC   
        """
    )

    with open("tmp/contest_results.csv", "w") as outfile:
        writer = DictWriter(
            outfile,
            fieldnames=[
                "contest_id",
                "contest",
                "contest_group",
                "contest_type",
                "non_partisan",
                "voter_nominated",
                "vote_for",
                "candidate_id",
                "name",
                "party",
                "total_votes",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def generate_precinct_results_csv(db):
    rows = db.query(
        """
        SELECT
        results.precinct_id,
        contests.id as contest_id,
        contests.name as contest,
        contests.[group] as contest_group,
        contests.type as contest_type,
        contests.non_partisan,
        contests.voter_nominated,
        contests.vote_for,
        candidates.id as candidate_id,
        candidates.name,
        candidates.party,
        results.polling_place,
        results.vote_by_mail,
        results.total
        FROM
        results
        JOIN candidates ON candidates.id = results.candidate_id
        JOIN contests ON contests.id = results.contest_id
        ORDER BY
        contests.id, results.precinct_id, candidates.id
        """
    )

    with open("tmp/precinct_results.csv", "w") as outfile:
        writer = DictWriter(
            outfile,
            fieldnames=[
                "precinct_id",
                "contest_id",
                "contest",
                "contest_group",
                "contest_type",
                "non_partisan",
                "voter_nominated",
                "vote_for",
                "candidate_id",
                "name",
                "party",
                "polling_place",
                "vote_by_mail",
                "total",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def run():
    db = Database("tmp/results.db")

    generate_contest_results_csv(db)
    generate_precinct_results_csv(db)


if __name__ == "__main__":
    run()

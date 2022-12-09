# LA County 2022 Election Results

A set of scripts for processing the 2022 LA County election results down to the precinct level. The results are available in CSV, JSON and SQLite/Spatialite formats. Data current as of LA County's Registar of Voters [Statement of Votes Cast release](https://www.lavote.gov/home/voting-elections/current-elections/election-results/past-election-results) on **Dec. 5, 2022**.

A **live** preview of the Spatialite database is available at on [my Datasette instance](https://datasette.rdmurphy.dev/la-county-election-results-2022). Explore and query the data live!

## Outputs

The following files are generated by the scripts and attached to the latest GitHub release:

| File                    | Notes                                                                                                                                                                                                                           |                                                                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `contest_results.csv`   | A CSV file containing the precinct-level results for each contest. Each row represents a candidate's results in a contest.                                                                                                      | [Download](https://github.com/rdmurphy/la-county-general-election-results-2022/releases/download/contest_results.csv)   |
| `precinct_results.csv`  | A CSV file containing the precinct-level results for each contest. Each row represents a candidate's result in a precinct in a contest.                                                                                         | [Download](https://github.com/rdmurphy/la-county-general-election-results-2022/releases/download/precinct_results.csv)  |
| `precinct_results.json` | A JSON file containing the precinct-level results for each contest. Each top-level object in the array represents a single contest. Each object includes contest metadata, a list of candidates and a list of precinct results. | [Download](https://github.com/rdmurphy/la-county-general-election-results-2022/releases/download/precinct_results.json) |
| `results.db`            | A SQLite database containing the precinct-level results. Includes `candidates`, `contests`, `precincts` and `results` tables.                                                                                                   | [Download](https://github.com/rdmurphy/la-county-general-election-results-2022/releases/download/results.db)            |
| `results_spatial.db`    | A Spatialite database containing the precinct-level results **and** precinct geometries. Includes `candidates`, `contests`, `precincts` and `results` tables.                                                                   | [Download](https://github.com/rdmurphy/la-county-general-election-results-2022/releases/download/results_spatial.db)    |

## Inputs

The following files are used to generate the precinct-level results and SQLite databases:

| File                          | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `counter_data.json`           | This file is found on the [dynamic updating results page](https://results.lavote.gov/#year=2022&election=4300). The candidate IDs that appear in this file are also found in `election_data.json`, making it possible to connect total votes to each candidate.                                                                                                                                                                                                         |
| `election_data.json`          | This file is found on the [dynamic updating results page](https://results.lavote.gov/#year=2022&election=4300). It gives every contest and candidate a unique ID. Despite having slots for vote counts these are always zeroed out, but the candidate IDs can be joined with the ones in `counter_data.json` to surface this value.                                                                                                                                     |
| `precincts.csv`               | A CSV representation of the precincts used for the 2022 general election. These are used to prepopulate the `precincts` table in the SQLite database. We do this separately from populating the `geometry` field to make loading results a bit quicker. This is sourced from the [Registrar Recorder Election Precincts](https://egis-lacounty.hub.arcgis.com/datasets/lacounty::registrar-recorder-election-precincts-/about) dataset found on the LA County GIS site. |
| `precincts.json`              | A GeoJSON representation of the precincts used for the 2022 general election. These are used to populate the `geometry` field in the `precincts` table in the the Spatialite database. This is sourced from the [Registrar Recorder Election Precincts](https://egis-lacounty.hub.arcgis.com/datasets/lacounty::registrar-recorder-election-precincts-/about) dataset found on the LA County GIS site.                                                                  |
| `statement_of_votes_cast.zip` | A ZIP file provided by the LA County Clerk that contains a precinct-level breakdown of results for each contest in Excel format.                                                                                                                                                                                                                                                                                                                                        |

## License

MIT

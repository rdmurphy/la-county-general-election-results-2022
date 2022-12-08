clean:
	rm -rf tmp/

run: clean
	pipenv run python prepare_dbs.py
	pipenv run python output_json.py
	pipenv run python output_csvs.py
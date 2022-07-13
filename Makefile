venv:
	rm -rf ./venv
	python3 -m venv venv
	. venv/bin/activate
	pip install -U -r requirements.txt

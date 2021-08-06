all: requirements run

requirements:
	pip install --disable-pip-version-check -r requirements.txt

# $i [ip_address]
run:
	python3 tracker.py $i

.PHONY: requirements run
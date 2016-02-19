.PHONY: all clean


venv:
	virtualenv-3.5 --clear --no-site-packages env3

clean:
	rm -rf env3
	find . -name *.pyc -exec rm '{}' \;


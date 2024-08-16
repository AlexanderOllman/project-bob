environment:
	(\
		echo "> Creating venv"; \
		python3 -m venv jyoti-core-venv; \
		source jyoti-core-venv/bin/activate; \
		echo "> Upgrade pip"; \
		jyoti-core-venv/bin/python3 -m pip install --upgrade pip; \
		echo "> Installing requirements"; \
		pip3 install -r requirements.txt; \
	)

clean:
	echo "> Removing virtual environment"; \
	deactivate; \
	rm -r jyoti-core-venv; \

serve:
	chmod +x ./run.sh
	./run.sh


install:
	echo argument is $(library); \
	source jyoti-core-venv/bin/activate; \
	pip3 install $(library); \
	pip3 freeze -l > requirements.txt; \

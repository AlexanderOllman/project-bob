# octo-innov-jyoti-core
Service handles the backend for project Jyoti. 
# Project Jyoti Internal POC Repository

This repository serves as the internal Proof of Concept (POC) for Project Jyoti, aimed at gaining a comprehensive understanding of LLM (Low-Level Machine) development. The project is divided into two main components:


### Prerequisites

1. Download python3 and install
2. Download brew 
3. Download pip3 using brew
4. Make sure pip3 and python3 works on the project path

### Execution guidlines

#### Set up the environment
```
make environment
```

#### activate virtual environment

```
source jyoti-core-venv/bin/activate
```
#### Running the service
```
make serve
```

#### Adding a new library. Please follow the below step
```
make install library='<l=ibrary name>'
example: make install library='psycopg2-binary'

pip3 freeze > requirements.txt

```

#### Terminating the service

```
cmd + c
```

#### Clean up 

```
deactivate; \
rm -r jyoti-core-venv; \
```

# project-bob

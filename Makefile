all: build

build:
	docker build . -t sieve:latest

pull:
	docker pull maxattax/sieve:latest
	docker tag maxattax/sieve:latest sieve:latest

push:
	docker tag sieve:latest maxattax/sieve:latest
	docker push maxattax/sieve:latest

check:
	docker run --rm sieve:latest check-sieve --help

test:
	docker run --rm sieve:latest sieve-test --help

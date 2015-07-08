build:
	docker build --force-rm -t $(shell basename $(CURDIR)) .
run:
	docker run -it $(shell basename $(CURDIR)) $(TOKEN)
rmi:
	docker rmi $(shell basename $(CURDIR))

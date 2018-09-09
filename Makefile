all:
	sudo docker build -t akoller/ehb2 . && sudo docker-compose -f docker-compose.yml -f docker-compose-private.yml up

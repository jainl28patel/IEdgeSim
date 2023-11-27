buildImage:
	@echo "------------------ Building Edge Network ------------------"
	cd ./CloudServer && docker build -t cloudserver .
	cd ./EdgeServer && docker build -t edgeserver .
	cd ./amqp && docker build -t amqp .
	cd ./CoAP && docker build -t coap .
	cd ./mqtt-simulator && docker build -t mqtt-simulator .
	cd ./HaLow && docker build -t halow .
	cd ./Zigbee && docker build -t zigbee .

runEdgeNetwork:
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name cloudserver cloudserver
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name edgeserver edgeserver
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name amqp amqp
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name coap coap
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name mqtt-simulator mqtt-simulator
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name halow halow
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name zigbee zigbee

runNormalNetwork:
	docker run -it --rm --network="host" -v "$(PWD)":/usr/src/app --name cloudserver cloudserver
	docker run -it --rm -p 9000:8000 -v "$(PWD)":/usr/src/app --name amqp amqp
	docker run -it --rm -p 9000:8000 -v "$(PWD)":/usr/src/app --name coap coap
	docker run -it --rm -p 9000:8000 -v "$(PWD)":/usr/src/app --name mqtt-simulator mqtt-simulator
	docker run -it --rm -p 9000:8000 -v "$(PWD)":/usr/src/app --name halow halow
	docker run -it --rm -p 9000:8000 -v "$(PWD)":/usr/src/app --name zigbee zigbee

clean:
	docker rm -f $(docker ps -a -q) | docker rmi -f $(docker images -q)

buildTest:
	cd ./CloudServer && docker build -t cloudserver .
	cd ./EdgeServer && docker build -t edgeserver .
	cd ./Zigbee && docker build -t zigbee .

runTest:
	docker run --rm --network="host" --name cloudserver cloudserver \
	& docker run --rm --network="host" -v "$(PWD)/EdgeServer:/usr/src/app" --name edgeserver edgeserver \
	& docker run -it --rm --network="host" -v "$(PWD)/Zigbee":/usr/src/app --name zigbee zigbee
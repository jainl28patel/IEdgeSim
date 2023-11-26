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
	docker run -it --rm --network="host" --name cloudserver cloudserver
	docker run -it --rm --network="host" --name edgeserver edgeserver
	docker run -it --rm --network="host" --name amqp amqp
	docker run -it --rm --network="host" --name coap coap
	docker run -it --rm --network="host" --name mqtt-simulator mqtt-simulator
	docker run -it --rm --network="host" --name halow halow
	docker run -it --rm --network="host" --name zigbee zigbee

runNormalNetwork:
	docker run -it --rm --network="host" --name cloudserver cloudserver
	docker run -it --rm -p 9000:8000 --name amqp amqp
	docker run -it --rm -p 9000:8000 --name coap coap
	docker run -it --rm -p 9000:8000 --name mqtt-simulator mqtt-simulator
	docker run -it --rm -p 9000:8000 --name halow halow
	docker run -it --rm -p 9000:8000 --name zigbee zigbee

clean:
	@echo "TODO"

removeImages:
	@echo "Removing Images"
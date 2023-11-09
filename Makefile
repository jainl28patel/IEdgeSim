buildCloudServer:
	@echo "Building Cloud Server"
	cd ./CloudServer && docker build -t cloud-server .
	pwd

buildEdgeNetwork:
	@echo "Building Edge Network"

buildNormalNetwork:
	@echo "Building Normal Network"
	cd ./NormalNetwork/iotnode && docker build -t normal-network .

runCloudServer:
	@echo "Running Cloud Server"
	docker run -it --rm --network="host" --name cloud-server cloud-server

runEdgeNetwork:
	@echo "Running Edge Network"

runNormalNetwork:
	@echo "Running Normal Network"
	docker run -it --rm --network="host" --name normal-network normal-network

runAll:
	@echo "TODO"

clean:
	@echo "TODO"

removeImages:
	@echo "Removing Images"
	docker image rm -f cloud-server | docker image rm -f normal-network
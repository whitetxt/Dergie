python3 main.py
rt=$?
while [[ $rt -ne 0 ]]
do
	python3 main.py
	rt=$?
done
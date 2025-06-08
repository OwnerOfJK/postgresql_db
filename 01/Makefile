build:
	cd ex00 && docker compose up --build

down:
	cd ex00 && docker compose down -v --remove-orphans

clean:
	cd ex00 && docker system prune -a --volumes

create:
	cd ex00 && python3 automatic_table.py ./customer
	cd ex00 && python3 automatic_table.py ./item

union:
	cd ex01 && python3 customers_table.py

duplicates:
	cd ex02 && python3 remove_duplicates.py

fusion:
	cd ex03 && python3 fusion.py

.PHONY: build down clean
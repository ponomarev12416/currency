CREATE TABLE IF NOT EXISTS stock(
	number       SERIAL        UNIQUE NOT NULL,
	order_number VARCHAR(14)   UNIQUE NOT NULL,
	cost_usd     DECIMAL(4, 2)        NOT NULL,
	cost_rub     DECIMAL(4, 2)        NOT NULL,
	supply_date  DATE                 NOT NULL,

	PRIMARY KEY (order_number)
);

INSERT INTO mineral_history (mineral_id, discovery_year_min, discovery_year_max)
VALUES ('e49ccbc5-3214-4f1f-846a-446f5fe7fca7', 1899, NULL),
    ('c7b7dddb-648f-456e-a74e-410b852bef8d', 1752, 1900),
	('790f05e5-97a9-45b1-9211-6b1b5af4e4cd', 1773, 1925),
	('ad66822c-526b-4a9e-bc11-b656c40f3f02', 1899, 1900),
	('34427527-4f24-4063-8833-fe5503287fcf', 1899, 1901);

DELETE FROM mineral_status WHERE mineral_id = '3b4131be-0640-4443-ae34-908587a511c8';
INSERT INTO mineral_status (mineral_id, status_id) VALUES ('3b4131be-0640-4443-ae34-908587a511c8', 5);
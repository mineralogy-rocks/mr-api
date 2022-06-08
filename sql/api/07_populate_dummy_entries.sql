INSERT INTO mineral_history (mineral_id, discovery_year_min, discovery_year_max)
VALUES ('e49ccbc5-3214-4f1f-846a-446f5fe7fca7', 1899, NULL),
    ('c7b7dddb-648f-456e-a74e-410b852bef8d', 1752, 1900),
	('790f05e5-97a9-45b1-9211-6b1b5af4e4cd', 1773, 1925),
	('ad66822c-526b-4a9e-bc11-b656c40f3f02', 1899, 1900),
	('34427527-4f24-4063-8833-fe5503287fcf', 1899, 1901);

DELETE FROM mineral_status WHERE mineral_id = '3b4131be-0640-4443-ae34-908587a511c8';
INSERT INTO mineral_status (mineral_id, status_id) VALUES ('3b4131be-0640-4443-ae34-908587a511c8', 5);
INSERT INTO mineral_status (mineral_id, status_id) VALUES ('37068d22-e699-4488-a67d-7e2282627175', 4), 
('6b9d1e7e-9bbf-49ce-bf1f-0ec73d2a2162', 4), ('8976b504-69a1-4161-b3bb-c8452f2ce9ca', 4), ('9d9b8c5f-ab06-47e3-b4c7-be8709ce52fb', 4), 
('3bc5bcc3-eeb8-46aa-98cf-a00fb8288651', 4), ('10f99e04-a05b-4358-accb-c0a31752a29b', 4), ('04d280af-da3a-4408-bf12-b2edc36afc14', 4);
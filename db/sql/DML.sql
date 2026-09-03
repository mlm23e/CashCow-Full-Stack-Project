INSERT INTO branches(name, location_region, capacity, supervisor_id) VALUES 
    ('Coastal Branch - Florida - Pensacola', 'US-South', 5, 1),
    ('City Branch - New York - Poughkeepsie', 'US-Northeast', 10, 4),
    ('City Branch - Wisconsin - Madison', 'US-Midwest', 7, 7),
    ('Community Branch - Montana - Great Falls', 'US-West', 3, 10);

UPDATE users
SET branch_id = CASE username
    WHEN 'admin' THEN 1
    WHEN 'technician' THEN 1
    WHEN 'auditor' THEN 1
    WHEN 'admin_carrie' THEN 2
    WHEN 'technician_carrie' THEN 2
    WHEN 'auditor_mike' THEN 2
    WHEN 'admin_john' THEN 3
    WHEN 'technician_james' THEN 3
    WHEN 'auditor_jamie' THEN 3
    WHEN 'admin_parmy' THEN 4
    WHEN 'technician_paul' THEN 4
    WHEN 'auditor_paul' THEN 4
END
WHERE role IN ('Operations Admin', 'Field Technician', 'Auditor')
    AND username IN (
    'admin',
    'technician',
    'auditor',
    'admin_carrie',
    'technician_carrie',
    'auditor_mike',
    'admin_john',
    'technician_james',
    'auditor_jamie',
    'admin_parmy',
    'technician_paul',
    'auditor_paul'
);

INSERT INTO atms(serial_number, model, branch_id, cash_level) VALUES
    ('RXA-7821', 'Halo II', 1, 100.00),
    ('FJ1-3420', 'Force', 1, 45.34),
    ('FJ1-3421', 'Force', 2, 12.33),
    ('FJ1-3422', 'Force', 2, 19.23),
    ('FJ1-5643', 'Force', 2, 20),
    ('FJ1-4564', 'Force', 3, 72.73),
    ('RXA-1234', 'Halo II', 3, 65),
    ('RXA-3421', 'Halo II', 4, 34),
    ('FJ1-2341', 'Force', 4, 32.22);

INSERT INTO service_calls(title, priority, status, atm_id, technician_id) VALUES 
    ('Fix Check Slot', 'Critical', 'In-Progress', 2, 2),
    ('Faulty Pin Pad', 'Critical', 'Completed', 3, 5),
    ('Broken Camera', 'Medium', 'Pending', 9, 11),
    ('Partially Damaged Screen', 'Low', 'Failed', 1, 2),
    ('Vandalized Console', 'Medium', 'In-Progress', 8, 8);


INSERT INTO diagnostic_reports(service_call_id, file_url, notes) VALUES 
    (2, 's3://cashcow-diagnostics/FJ1-3421-001.txt', 'Pin Pad Signals OK');


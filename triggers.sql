-- Trigger per prevenire overlap tra i voli
CREATE OR REPLACE FUNCTION prevent_airplane_overlap() 
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM Flights
        WHERE
        airplane_id = NEW.airplane_id AND
        NEW.departure_time < arrival_time AND
        NEW.arrival_time > departure_time
    ) THEN
        RAISE EXCEPTION 'Errore: sovrapposizione di voli per lo stesso aereo.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;#

CREATE OR REPLACE TRIGGER trigger_overlap
BEFORE INSERT ON Flights
FOR EACH ROW
EXECUTE FUNCTION prevent_airplane_overlap();#
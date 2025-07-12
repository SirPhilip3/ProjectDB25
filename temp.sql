CREATE OR REPLACE FUNCTION check_seat_availability()
RETURNS trigger AS $$
DECLARE
    airplane_seats integer;
    sold_seats integer;
BEGIN
    -- Ottieni i posti dell'aereo per la classe specifica
    SELECT CASE 
        WHEN NEW.ticket_class = 'economy' THEN a.economy_seats
        WHEN NEW.ticket_class = 'business' THEN a.business_seats
        WHEN NEW.ticket_class = 'first_class' THEN a.first_class_seats
        ELSE 0
    END INTO airplane_seats
    FROM flights f
    JOIN airplanes a ON f.airplane_id = a.id
    WHERE f.id = NEW.flight_id;
    
    -- Conta i biglietti gia venduti per questa classe
    SELECT COUNT(*) INTO sold_seats
    FROM tickets t
    WHERE t.flight_id = NEW.flight_id 
    AND t.ticket_class = NEW.ticket_class
   
    -- Controlla se ci sono posti disponibili
    IF sold_seats >= airplane_seats THEN
        RAISE EXCEPTION 'No seats available for class % on flight %', NEW.ticket_class, NEW.flight_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- -- Trigger che si attiva PRIMA di inserire una prenotazione
-- CREATE OR REPLACE TRIGGER trigger_check_seat_availability
--     BEFORE INSERT ON Flights
--     FOR EACH ROW
--     EXECUTE FUNCTION check_seat_availability();#


--! Trigger per verificare la disponibilità dei posti , da rivedere con il modello
-- CREATE OR REPLACE FUNCTION check_seat_availability()
-- RETURNS trigger AS $$
-- DECLARE
--     available_seats integer;
-- BEGIN
--     SELECT CASE 
--         WHEN NEW.class_type = 'economy' THEN available_economy_seats
--         WHEN NEW.class_type = 'business' THEN available_business_seats  
--         WHEN NEW.class_type = 'first_class' THEN available_first_class_seats
--     END INTO available_seats
--     FROM flights 
--     WHERE id = NEW.flight_id;
    
--     IF available_seats <= 0 THEN
--         RAISE EXCEPTION 'No seats available for class type % on flight %', NEW.class_type, NEW.flight_id;
--     END IF;
    
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;#

-- -- Trigger che si attiva PRIMA di inserire una prenotazione
-- CREATE OR REPLACE TRIGGER trigger_check_seat_availability
--     BEFORE INSERT ON Flights
--     FOR EACH ROW
--     EXECUTE FUNCTION check_seat_availability();#



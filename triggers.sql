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
    AND t.ticket_class = NEW.ticket_class;
   
    -- Controlla se ci sono posti disponibili
    IF sold_seats >= airplane_seats THEN
        RAISE EXCEPTION 'No seats available for class % on flight %', NEW.ticket_class, NEW.flight_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;#


-- Trigger che si attiva PRIMA di inserire una prenotazione
CREATE OR REPLACE TRIGGER trigger_check_seat_availability
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION check_seat_availability();#

-- trigger per notificare la disponibilità dei posti
CREATE OR REPLACE FUNCTION notify_seat_availability()
RETURNS trigger AS $$
DECLARE
    airplane_economy integer;
    airplane_business integer;
    airplane_first integer;
    sold_economy integer := 0;
    sold_business integer := 0;
    sold_first integer := 0;
    safe_flight_id text;
    target_flight_id text;
    operation_type text;
    affected_class text;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_flight_id := OLD.flight_id;
        affected_class := OLD.ticket_class;
        operation_type := 'DELETE';
    ELSE
        target_flight_id := NEW.flight_id;
        affected_class := NEW.ticket_class;
        operation_type := TG_OP;
    END IF;

    -- Ottieni i posti dell'aereo per tutte le classi
    SELECT a.economy_seats, a.business_seats, a.first_class_seats
    INTO airplane_economy, airplane_business, airplane_first
    FROM flights f
    JOIN airplanes a ON f.airplane_id = a.id
    WHERE f.id = target_flight_id;

    -- Conta i biglietti già venduti per ogni classe 
    SELECT 
        COALESCE(SUM(CASE WHEN ticket_class = 'economy' THEN 1 ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN ticket_class = 'business' THEN 1 ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN ticket_class = 'first_class' THEN 1 ELSE 0 END), 0)
    INTO sold_economy, sold_business, sold_first
    FROM tickets t
    WHERE t.flight_id = target_flight_id;
    
    safe_flight_id := REPLACE(target_flight_id, '-', '_');
    PERFORM pg_notify('seat_availability_' || safe_flight_id, 
        json_build_object(
            'flight_id', target_flight_id,
            'economy_available', airplane_economy - sold_economy,
            'business_available', airplane_business - sold_business,
            'first_class_available', airplane_first - sold_first,
            'total_available', (airplane_economy - sold_economy) + (airplane_business - sold_business) + (airplane_first - sold_first),
            'updated_class', affected_class,
            'operation', operation_type
        )::text
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;#


-- Trigger che si attiva PRIMA di inserire una prenotazione
CREATE OR REPLACE TRIGGER trigger_notify_seat_availability
    AFTER INSERT OR DELETE OR UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION notify_seat_availability();#

import json
import time

from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

import pika
import os
from datetime import datetime, timedelta, UTC
from frcm.frcapi import METFireRiskAPI
from frcm.datamodel.model import Location
import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("IP"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=5432
    )

def main():
    while True: 
        start = time.time()

        ip = os.getenv("IP")
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip))
        channel = connection.channel()

        channel.exchange_declare(exchange="fire_risk", exchange_type="topic")
        with get_connection() as conn:
            with conn.cursor() as cursor:

                now = datetime.now(UTC)

                cursor.execute("SELECT id, name, latitude, longitude  FROM city")
                cities = cursor.fetchall()

                frc = METFireRiskAPI()
                obs_delta = timedelta(days = 1)

                for city in cities:
                    location = Location(latitude=city[2], longitude=city[3])
                    predictions = frc.compute_now(location, obs_delta)
                    
                    # Should find the first "future" TTF
                    first_future = next(
                        (e for e in predictions.firerisks if e.timestamp > now), None
                    )
                    
                    if first_future is not None:    
                        message = {
                            "city_id": city[0],
                            "city_name": city[1],
                            "timestamp": first_future.timestamp.isoformat(),
                            "ttf": first_future.ttf,
                            "wind_speed": first_future.wind_speed
                            }
                        
                        channel.basic_publish(
                            exchange="fire_risk",
                            routing_key=city[1].lower(),
                            body=json.dumps(message)
                            )

                    values = [
                        (
                            city[0],
                            e.timestamp,
                            e.ttf,
                            e.wind_speed,
                            e.timestamp > now
                        )
                        for e in predictions.firerisks
                    ]

                    cursor.executemany(
                        """
                        INSERT INTO fire_risk (city_id, timestamp, ttf, wind_speed, is_forecast)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (city_id, timestamp)
                        DO UPDATE SET
                            ttf = EXCLUDED.ttf,
                            wind_speed = EXCLUDED.wind_speed,
                            is_forecast = EXCLUDED.is_forecast,
                            created_at = NOW()
                        """,
                        values
                    )

        print("Message sent")
        connection.close()
        
        elapsed = time.time() - start
        sleep_time = max(0, 3600 - elapsed)

        time.sleep(sleep_time)

if __name__ == "__main__":
    main()

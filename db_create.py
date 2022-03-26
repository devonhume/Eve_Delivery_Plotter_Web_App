from init import app, db
import csv


from db_handler import Jump, System, User, Agent, Mission, Character, Save


db.create_all()
db.session.commit()

with open('mapSolarSystems.csv', mode='r') as file:
    reader = csv.reader(file)
    i = 0
    for row in reader:
        if i > 0:
            system = System(
                system_id=int(row[2]),
                system_name=row[3]
            )
            db.session.add(system)
            db.session.commit()
        i += 1

with open('mapSolarSystemJumps.csv', mode='r') as file:
    reader = csv.reader(file)
    i = 0
    for row in reader:
        if i > 0:
            jump = Jump(
                fromsystem_id=int(row[2]),
                tosystem_id=int(row[3]),
            )
            db.session.add(jump)
            db.session.commit()
        i += 1

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from init import db, login_manager
from flask_login import UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash


association_table = db.Table('association', db.metadata,
                             db.Column('characters_id', db.ForeignKey('characters.id'), primary_key=True),
                             db.Column('agents_id', db.ForeignKey('agents.id'), primary_key=True),
                             db.Column('missions_id', db.ForeignKey('missions.id'), primary_key=True),
                             )


class DbHandler():

    def __init__(self, database):
        self.db = database

    def get_user(self, id=None, username=None):
        if id:
            user = User.query.filter_by(id=id).first()
        elif username:
            user = User.query.filter_by(username=username). first()
        return user

    def authenticate_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user:
            user_password = user.password
            if check_password_hash(user_password, password):
                return user.id
            else:
                return 'pass_fail'
        else:
            return 'email_fail'

    def log_in_user(self, user_id):
        login_user(self.get_user(id=user_id))

    def register_user(self, name, email, password):
        user = User(
            username=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(user)
        db.session.commit()
        return user.id

    def get_agent(self, agentname):
        agent = Agent.query.filter_by(name=agentname).first()
        return agent

    def check_system(self, system_name):
        system = System.query.filter_by(system_name=system_name).first()
        if system:
            return True
        else:
            return False

    def check_agent(self, agent_name):
        agent = Agent.query.filter_by(name=agent_name).first()
        if agent:
            return True
        else:
            return False

    def get_mission(self, mission_id):
        mission = Mission.query.get(mission_id)
        return mission

    def delete_mission(self, mission_id):
        mission = Mission.query.get(mission_id)
        self.db.session.delete(mission)
        self.db.session.commit()

    def get_character(self, char_name):
        return Character.query.filter_by(name=char_name).first()

    def get_char_system(self, char_name):
        char = Character.query.filter_by(name=char_name).first()
        return char.current_system

    def set_char_system(self, char_name, system):
        char = Character.query.filter_by(name=char_name).first()
        char.current_system = system
        db.session.commit()

    def create_agent(self, name, system):
        agent = Agent(
            name=name,
            system=system
        )
        db.session.add(agent)
        db.session.commit()
        return agent

    def get_system_id(self, system_name):
        print(f"get_system_id: {system_name}")
        system = System.query.filter_by(system_name=system_name).first()
        return system.system_id

    def get_system_name(self, system_id):
        system = System.query.filter_by(system_id=system_id).first()
        return system.system_name

    def get_gates(self, system_id):
        gates = Jump.query.filter_by(fromsystem_id=system_id).all()
        gate_list = []
        for gate in gates:
            gate_list.append(gate.tosystem_id)
        return gate_list


class Jump(db.Model):
    __tablename__ = 'jumps'
    id = db.Column(db.Integer, primary_key=True)
    fromsystem_id = db.Column(db.Integer, nullable=False)
    tosystem_id = db.Column(db.Integer, nullable=False)


class System(db.Model):
    __tablename__ = 'systems'
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, nullable=False)
    system_name = db.Column(db.String(100), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    account_type = db.Column(db.String(50), nullable=False, default='user')
    characters = relationship('Character', back_populates='user')


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    current_system = db.Column(db.String(100), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='characters')
    missions = relationship('Mission', secondary=association_table, back_populates='characters')
    agents = relationship('Agent', secondary=association_table, back_populates='characters')
    save = relationship('Save', uselist=False, back_populates='character')


class Agent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    system = db.Column(db.String(100), nullable=False)
    characters = relationship('Character', secondary=association_table, back_populates='agents')
    missions = relationship('Mission', secondary=association_table, back_populates='agent')


class Mission(db.Model):
    __tablename__ = 'missions'
    id = db.Column(db.Integer, primary_key=True)
    start_system = db.Column(db.String(100), nullable=False)
    destination_system = db.Column(db.String(100), nullable=False)
    agent = relationship('Agent', secondary=association_table, back_populates='missions')
    characters = relationship('Character', secondary=association_table, back_populates='missions')


class Save(db.Model):
    __tablename__ = 'saves'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.VARCHAR, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character = relationship('Character', back_populates='save')

from evedplot import *
import random
import json
import db_handler


class Plotter():

    def __init__(self, dbhandler, character=None):
        self.dbhandler = dbhandler
        self.character = character
        self.current_system = None
        self.current_goal = None
        self.jump_to = None
        self.agents = {}
        self.missions = {}
        # system_names = SYSTEMS['SOLARSYSTEMNAME'].tolist()
        self.player = Player(self.current_system)

    def set_character(self, character):
        self.character = self.dbhandler.get_character(character)
        return

    def set_current_system(self, current_sys_input):

        # Bring in global variable
        # global current_system

        # Get System from box
        # cur_sys_input = current_system_entry.get().title()

        # Check if real system
        check = self.dbhandler.check_system(current_sys_input)
        if not check:
            return False
        else:
            # Update self.current_system
            self.current_system = current_sys_input
            self.character.current_system = self.current_system
            # Update Player
            print(f"Current System: {self.current_system}")
            self.player.update_system(self.current_system)
            # Call update
            self.update_current_system()
            return


    def update_current_system(self):
        # global jump_to

        # Update Current Jump Path

        print(f"Agents: {self.agents}, \nMissions: {self.missions}")
        if self.agents or self.missions:
            # Update Jumps
            if self.agents:
                self.refresh_agents()
            if self.missions:
                self.refresh_missions()
            jump_data = self.player.get_next_jump(self.agents, self.missions)
            print(f"jump_to changed from {self.jump_to} to {jump_data[2]}; data returned: {jump_data}")
            self.jump_to = jump_data[2]

            self.update_goal()

        # # Update Label
        # cur_sys_label.config(text=f"CURRENT SYSTEM: {current_system}")
        # # Reset entry box
        # current_system_entry.delete(0, tk.END)


    def add_agent(self, agent_name, jumps):
        # Get Agent from Database
        new_agent = self.dbhandler.get_agent(agent_name)

        # agent_name = agent_name_entry.get().title()

        # Check if agent already in list
        is_there = False
        for agent in self.agents:
            if self.agents[agent].name_match(agent_name):
                is_there = True

        # Get Agent's System from box
        # agent_system = agent_system_entry.get().title()

        # Check to see if real system - cancel entry if not
        # if agent_system not in system_names:
        #     messagebox.showinfo(message=f"{agent_system} is not a known system.")
        #     return

        if not self.dbhandler.check_system(new_agent.system):
            print(f"{new_agent.system} is not a known system.")
            return f"{new_agent.system} is not a known system."

        # If Agent already in list cancel entry
        elif is_there:
            print(f"{agent_name} already exists.")
            return f"{agent_name} already exists."

        # Add new agent to list
        else:
            # Get Jumps from box
            # agent_jumps = int(agent_jumps_entry.get())
            # agent_jumps = new_agent.jumps

            # Add new
            self.agents[agent_name] = Agent(new_agent.name, new_agent.system, jumps)

            # Call Refresh
            self.refresh_agents()

            # update save file
            self.save_data()

            # Reset Entry Boxes
            # agent_name_entry.delete(0, tk.END)
            # agent_name_entry.insert(tk.END, string="Agent Name")
            # agent_system_entry.delete(0, tk.END)
            # agent_system_entry.insert(tk.END, string="Agent System")
            # agent_jumps_entry.delete(0, tk.END)
            # agent_jumps_entry.insert(tk.END, string="Jumps")
            return


    def add_mission(self, miss_id):

        # # Get info from boxes
        # miss_agent = mission_agent_entry.get()
        # miss_dest = mission_destination_entry.get()
        # miss_jumps = int(mission_jumps_entry.get())

        # Get Mission From Database
        mission = self.dbhandler.get_mission(miss_id)

        # Check system entry
        if not self.dbhandler.check_system(mission.destination_system):
            print(f"{mission.destination_system} is not a known system.")
            return f"{mission.destination_system} is not a known system."

        # Check to see if Mission Agent exists
        if not self.dbhandler.check_agent(mission.agent):
            print(f"Please add {mission.agent} as an Agent.")
            return f"Please add {mission.agent} as an Agent."

        # Create Mission ID
        # rand_id = random.randint(10000, 99999)
        # while rand_id in self.missions:
        #     rand_id = random.randint(10000, 99999)

        # Add New Mission to Missions global dict
        new_mission = Mission(mission.agent, mission.destination_system, mission.id, mission.jumps)
        self.missions[mission.id] = new_mission

        # Add Mission to Agent's mission list, set Agent's status to Active
        self.agents[mission.agent].add_mission(new_mission)

        # Update save file
        self.save_data()

        # Refresh agents and missions
        self.refresh_agents()
        self.refresh_missions()

        # # Reset Entry Boxes
        # mission_agent_entry.delete(0, tk.END)
        # mission_agent_entry.insert(tk.END, string="Mission Agent")
        # mission_destination_entry.delete(0, tk.END)
        # mission_destination_entry.insert(tk.END, string="Destination")
        # mission_jumps_entry.delete(0, tk.END)
        # mission_jumps_entry.insert(tk.END, string="Jumps")

        return


    def complete_mission(self, m_id):

        # Get info from boxes
        # m_id = int(mission_id_entry.get())
        m_agent = self.missions[m_id].agent

        # call Complete Mission on mission agent
        self.agents[m_agent].complete_mission(m_id)

        # Remove Mission from Missions global dict
        del self.missions[m_id]
        self.dbhandler.delete_mission(m_id)

        # Refresh agents and missions
        self.refresh_agents()
        self. refresh_missions()

        # Update Save File
        self.save_data()


    def activate_agent(self, agent):

        # Check if Agent exists
        if agent not in self.agents:
            print(f"{agent} is not an Agent.")
            return
        else:
            # Set agent status
            self.agents[agent].status = "waiting"

            # Refresh agents
            self.refresh_agents()

            # Update Save File
            self.save_data()
            return

    def remove_agent(self, agent):

        # Set agent status
        self.agents[agent].status = "inactive"

        # Refresh agents
        self.refresh_agents()

        # Update Save File
        self.save_data()
        return


    def refresh_agents(self):

        # Create a list for waiting agents
        waiting_agents = []

        # Create output strings
        wait_agents = []
        wait_systems = ""

        # Calculate path for each waiting agent
        # Append to wait list (name, system) for each agent
        for agent in self.agents:
            print(agent)
            if self.agents[agent].status == "waiting":
                self.player.make_path(self.agents[agent].system, self.agents[agent].jumps)
                waiting_agents.append(self.agents[agent].wait_stats())

        # Update Goal
        if waiting_agents:
            self.update_goal()

        # Build output strings
        for item in waiting_agents:
            # wait_agents += item[0] + "\n"
            # wait_systems += str(item[1]) + "|" + item[2] + "\n"
            wait_agents.append({'agent': item[0], 'system': item[2], 'jumps': item[1]})

        # # Delete and update display boxes
        # waiting_agents_agent_textbox.delete('1.0', tk.END)
        # waiting_agents_agent_textbox.insert(tk.END, wait_agents)
        # waiting_agents_system_textbox.delete('1.0', tk.END)
        # waiting_agents_system_textbox.insert(tk.END, wait_systems)

        return wait_agents


    def refresh_missions(self):

        # Create Output Strings
        act_id = ""
        act_agents = ""
        act_dest = ""

        act_missions = []

        # Calculate path for each waiting agent
        # Populate Output Strings
        for mission in self.missions:
            self.player.make_path(self.missions[mission].system, self.missions[mission].jumps)
            # act_id += str(self.missions[mission].missionid) + "\n"
            # act_agents += self.missions[mission].agent + "\n"
            # act_dest += str(self.missions[mission].jumps) + "|" + self.missions[mission].system + "\n"
            act_missions.append({
                'id': self.missions[mission].missionid,
                'agent': self.missions[mission].agent,
                'destination': self.missions[mission].system,
                'jumps': self.missions[mission].jumps
            })

        # Update Current Goal
        self.update_goal()

        # # Delete and update display boxes
        # active_missions_id_textbox.delete('1.0', tk.END)
        # active_missions_id_textbox.insert(tk.END, act_id)
        # active_missions_agent_textbox.delete('1.0', tk.END)
        # active_missions_agent_textbox.insert(tk.END, act_agents)
        # active_missions_destination_textbox.delete('1.0', tk.END)
        # active_missions_destination_textbox.insert(tk.END, act_dest)

        return act_missions

    def jump(self):

        # global current_system
        # global jump_to

        print(f"{self.current_system} changed to {self.jump_to}")
        self.current_system = self.jump_to
        # Update Player
        print(f"Current System: {self.current_system}")
        self.player.update_system(self.current_system)
        self.player.update_jumps(self.agents)
        self.player.update_jumps(self.missions)
        self.update_current_system()
        return


    def update_goal(self):

        # global current_goal
        new_data = self.player.get_next_jump(self.agents, self.missions)

        if not new_data:
            print("No Agents of Missions")
            return

        self.current_goal = new_data[1]
        self.player.goal = self.current_goal
        if self.current_system == self.current_goal:
            print(f"Current Destination: !!{self.current_goal}!!")
        else:
            print(f"Current Destination: {self.current_goal}")
        print(f"Distance: {new_data[0]}")
        return


    def save_data(self):

        # Create save dict for agents
        agent_dict = {}
        # get save data for each agent
        for agent in self.agents:
            agent_dict[agent] = self.agents[agent].save_dump()

        # Create save dict for missions
        mission_dict = {}
        # get save data from each mission
        for mission in self.missions:
            mission_dict[mission] = self.missions[mission].save_dump()

        # Create Master Dict to write to JSON file
        save_dict = {
            "current_system": self.current_system,
            "agents": agent_dict,
            "missions": mission_dict
        }

        # Write Master Dict to File
        with open("evedplot_save.json", mode="w") as file:
            json.dump(save_dict, file, indent= 4)

        return


    def load_data(self):

        # # Global Variables to Set
        # global current_system
        # global agents
        # global missions

        try:
            # load JSON from file as dict
            with open("evedplot_save.json", mode="r") as file:
                load_dict = json.load(file)

        except json.decoder.JSONDecodeError:
            pass

        else:
            # Set Current System
            self.current_system = load_dict['current_system']
            # Update Player
            print(f"Current System: {self.current_system}")
            self.player.update_system(self.current_system)
            self.update_current_system()

            # Repopulate Agents
            for agent in load_dict['agents']:
                new_agent = Agent(
                    load_dict['agents'][agent]['name'],
                    load_dict['agents'][agent]['system'],
                    load_dict['agents'][agent]['jumps'],
                    load_dict['agents'][agent]['status'],
                )
                self.agents[new_agent.name] = new_agent
            self.refresh_agents()

            # Repopulate Missions
            for mission in load_dict['missions']:
                new_mission = Mission(
                    load_dict['missions'][mission]['agent'],
                    load_dict['missions'][mission]['destination'],
                    load_dict['missions'][mission]['missionid'],
                    load_dict['missions'][mission]['jumps']
                )
                self.missions[new_mission.missionid] = new_mission
                self.agents[load_dict['missions'][mission]['agent']].add_mission(new_mission)
            self.refresh_missions()

            self.update_current_system()

    def reset(self):
        self.character = None
        self.current_system = None
        self.current_goal = None
        self.jump_to = None
        self.agents = {}
        self.missions = {}
        # system_names = SYSTEMS['SOLARSYSTEMNAME'].tolist()
        self.player = Player(self.current_system)
        return
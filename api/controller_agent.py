from api.agent import Agent


class ControllerAgent(Agent):
    def get_action(self, game) -> int:
        return input('Action: ')
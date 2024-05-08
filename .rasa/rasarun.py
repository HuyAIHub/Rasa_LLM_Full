from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.agent import Agent

interpreter = RasaNLUInterpreter("/home/oem/Documents/VCC/rasachat/rasachatgpt/models")
agent = Agent.load("/home/oem/Documents/VCC/rasachat/rasachatgpt/models", interpreter=interpreter)

def run_rasa_shell(input_text):
    responses = agent.handle_text(input_text)
    for response in responses:
        print(response.get("text"))

while True:
    user_input = input("User: ")
    run_rasa_shell(user_input)
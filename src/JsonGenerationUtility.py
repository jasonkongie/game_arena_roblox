import json
Messages = []
with open("../GenerationTemplates/template.json", mode="r") as file:
    Messages = json.load(file)

print(Messages)
ChatLogString = ""
while True:
    nickname = input("Nickname: ")
    text = input("Text: ")
    if nickname == "" or text == "":
        break
    ChatLogString += f"\n{nickname}: {text}"
Messages.append({"role": "user", "content": ChatLogString})

answer = input("Answer: ")
Messages.append({"role": "assistant", "content": answer})
with open("../GenerationTemplates/template.json", mode="w") as file:
    json.dump(Messages, file)

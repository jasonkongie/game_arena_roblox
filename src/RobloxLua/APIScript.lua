local BotName = "Pepe"
local LogSize = 20
local AnswerEverynMessages = 1
local NonAnsweredMessages = AnswerEverynMessages - 1
local HttpService = game:GetService("HttpService")
local ChatService = game:GetService("Chat")
local AppUrl = "YOUR URL HERE"
Log = {}

function ClearTable(tbl, AmmountToKeep)
	local keepCount = math.min(AmmountToKeep, #tbl)

	for i = 1, #tbl - keepCount do
		table.remove(tbl, 1)
	end
end


function HandleMessage(Player, Message)
	table.insert(Log, {nickname = Player.name, content = Message})
	NonAnsweredMessages += 1
	if NonAnsweredMessages >= AnswerEverynMessages then
		ClearTable(Log, LogSize)
		NonAnsweredMessages = 0
		local response = HttpService:PostAsync(AppUrl, HttpService:JSONEncode(Log), Enum.HttpContentType.ApplicationJson, false)
		game.ReplicatedStorage.ClientSendMsg:FireAllClients(BotName, response)
		table.insert(Log, {nickname = BotName, content = response})
		ChatService:Chat(script.Parent.Head, response)
	end
end

game.Players.PlayerAdded:Connect(function(Player)
	Player.Chatted:Connect(function(Message)
		HandleMessage(Player, Message)
	end)
end)


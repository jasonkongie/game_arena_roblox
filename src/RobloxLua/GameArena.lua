-- Server Script

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ChatService = game:GetService("Chat")

local AppUrl = "https://9618-70-95-161-188.ngrok-free.app"  -- Replace with your actual ngrok URL
local BotName = "PePe"
local LogSize = 20
local AnswerEverynMessages = 1
local NonAnsweredMessages = AnswerEverynMessages - 1
local Log = {}

local playerSessions = {}
local ChatMessageEvent = Instance.new("RemoteEvent", ReplicatedStorage)
ChatMessageEvent.Name = "ChatMessage"

-- Function to clear the Log
local function ClearTable(tbl, AmmountToKeep)
	local keepCount = math.min(AmmountToKeep, #tbl)

	for i = 1, #tbl - keepCount do
		table.remove(tbl, 1)
	end
end

-- Function to send AI message as "PePe"
local function SendMessageAsPepe(player, message)
	print("Sending message as PePe:", message)

	-- Fire message to all clients
	game.ReplicatedStorage.ClientSendMsg:FireAllClients(BotName, message)

	-- Add PePe's response to the log
	table.insert(Log, {nickname = BotName, content = message})

	--Pepe is sending a message
	ChatService:Chat(script.Parent.Head, message)
end

-- Function to send player's message
local function sendMessageAsPlayer(player, message)
	print("Sending message as Player:", message)

	-- Fire message to all clients as Player
	game.ReplicatedStorage.ClientSendMsg:FireAllClients(player.Name, message)

	-- Add Player's response to the log
	table.insert(Log, {nickname = player.Name, content = message})

	-- Display Player's message in chat
	if player.Character and player.Character:FindFirstChild("Head") then
		ChatService:Chat(player.Character.Head, message, Enum.ChatColor.White)
	end
end

-- Function to send post request
local function sendPostRequest(url, requestBody)
	print("Sending POST request to the server. URL:", url)
	local success, response = pcall(function()
		return HttpService:PostAsync(
			url,
			requestBody,
			Enum.HttpContentType.ApplicationJson,  -- This automatically sets Content-Type
			false  -- compress
		)
	end)

	if success then
		print("POST request successful.")
		return response
	else
		print("POST request failed.")
		warn(response)
		return nil
	end
end



-- Function to start the game for a player
local function startGameForPlayer(player)
	print("Starting game for player:", player.Name)

	local response = sendPostRequest(AppUrl .. "/start_game", "")
	if response then
		local data = HttpService:JSONDecode(response)
		local sessionId = data.session_id
		local aiMessage = data.system_prompt

		print("Session ID:", sessionId)
		print("AI Initial Message:", aiMessage)

		playerSessions[player.UserId] = {
			sessionId = sessionId,
			gameOver = false
		}

		-- Send AI message to the player as "PePe"
		SendMessageAsPepe(player, aiMessage)
		
	else
		print("Failed to start game for player:", player.Name)
	end
end

-- Function to handle player chat messages
local function onPlayerChatted(player)
	player.Chatted:Connect(function(message)
		print("Player", player.Name, "sent message:", message)
		local lowerMessage = message:lower()

		if lowerMessage == "start game" then
			print("Player " .. player.Name .. " is starting a game.")
			startGameForPlayer(player)
			return
		end

		local session = playerSessions[player.UserId]
		if not session or session.gameOver then
			print("No active session for player:", player.Name)
			-- Inform the player that the game is not started or is over
			ChatMessageEvent:FireClient(player, BotName, "Game is not started. Type 'Start Game' to begin.")
			return
		end

		-- Send player's response to the server
		local url = AppUrl .. "/ask_question?session_id=" .. session.sessionId
		local requestBody = HttpService:JSONEncode({
			user_response = message
		})

		local response = sendPostRequest(url, requestBody)
		if response then
			local data = HttpService:JSONDecode(response)
			local aiMessage = data.ai_message
			session.gameOver = data.game_over

			print("AI Response:", aiMessage)
			print("Is game over:", session.gameOver)

			-- Send AI message to the player as "PePe"
			SendMessageAsPepe(player, aiMessage)

			-- If game is over, inform the player
			if session.gameOver then
				ChatMessageEvent:FireClient(player, BotName, "Game over! Thanks for playing.")
				-- Remove the session
				playerSessions[player.UserId] = nil
			end
		else
			print("Failed to send user response for player:", player.Name)
		end
	end)
end

-- Connect the functions to player events
Players.PlayerAdded:Connect(function(player)
	print("Player added:", player.Name)
	onPlayerChatted(player)
end)

Players.PlayerRemoving:Connect(function(player)
	print("Player removing:", player.Name)
	-- Clean up any session data
	playerSessions[player.UserId] = nil
end)
local PathFindingService = game:GetService("PathfindingService")



local npc = script.Parent
local humanoid = npc.Humanoid
local PrimaryPart = npc.PrimaryPart
local animator = humanoid.Animator
local WalkAnim = script.walk.WalkAnim
local WalkTrack = animator:LoadAnimation(WalkAnim)
local IdleAnim = script.idle.Animation1
local IdleTrack = animator:LoadAnimation(IdleAnim)
local RandomXMin = -50
local RandomZMin = -50
local RandomXMax = 50
local RandomZMax = 50
PrimaryPart:SetNetworkOwner(nil)


while true do
	IdleTrack:Play()
	wait(math.random(0.2, 5))
	IdleTrack:Stop()
	local path = PathFindingService:CreatePath()
	RandomVector = Vector3.new(math.random(RandomXMin, RandomXMax), PrimaryPart.Position.Y, math.random(RandomZMin, RandomZMax))
	path:ComputeAsync(PrimaryPart.Position, RandomVector)
	local waypoints = path:GetWaypoints()
	WalkTrack:Play()
	for i, waypoint in pairs(waypoints) do
		humanoid:MoveTo(waypoint.Position)
		humanoid.MoveToFinished:Wait(2)
	end
	WalkTrack:Stop()
end
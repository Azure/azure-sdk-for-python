
param projectWorkspaceId string

var part1 = substring(projectWorkspaceId, 0, 8)    // First 8 characters
var part2 = substring(projectWorkspaceId, 8, 4)    // Next 4 characters
var part3 = substring(projectWorkspaceId, 12, 4)   // Next 4 characters
var part4 = substring(projectWorkspaceId, 16, 4)   // Next 4 characters
var part5 = substring(projectWorkspaceId, 20, 12)  // Remaining 12 characters

var formattedGuid = '${part1}-${part2}-${part3}-${part4}-${part5}'

output projectWorkspaceIdGuid string = formattedGuid

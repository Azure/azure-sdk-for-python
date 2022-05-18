param(
  # The repo owner: e.g. Azure
  $RepoOwner,
  # The repo name. E.g. azure-sdk-for-java
  $RepoName,
  # Please use the RepoOwner/RepoName format: e.g. Azure/azure-sdk-for-java
  $RepoId="$RepoOwner/$RepoName",
  # CentralRepoId the original PR to generate sync PR. E.g Azure/azure-sdk-tools for eng/common
  $CentralRepoId,
  # We start from the sync PRs, use the branch name to get the PR number of central repo. E.g. sync-eng/common-(<branchName>)-(<PrNumber>). Have group name on PR number.
  [Parameter(Mandatory = $true)]
  $CentralPRRegex,
  # Date format: e.g. Tuesday, April 12, 2022 1:36:02 PM. Allow to use other date format.
  [AllowNull()]
  [DateTime]$LastCommitOlderThan,
  [Parameter(Mandatory = $true)]
  $AuthToken
)

. (Join-Path $PSScriptRoot common.ps1)

function RetrievePRAndClose($pullRequestNumber)
{
  try {
    $centralPR = Get-GitHubPullRequest -RepoId $CentralRepoId -PullRequestNumber $pullRequestNumber -AuthToken $AuthToken
    if ($centralPR.state -eq "closed") {
      return
    }
  }
  catch 
  {
    LogError "Get-GitHubPullRequests failed with exception:`n$_"
    exit 1
  }
  
  try {
    $head = "${RepoId}:${branchName}"
    LogDebug "Operating on branch [ $branchName ]"
    $pullRequests = Get-GitHubPullRequests -RepoId $RepoId -State "all" -Head $head -AuthToken $AuthToken
  }
  catch
  {
    LogError "Get-GitHubPullRequests failed with exception:`n$_"
    exit 1
  }
  $openPullRequests = $pullRequests | ? { $_.State -eq "open" }

  foreach ($openPullRequest in $openPullRequests) {
    try 
    {
      Close-GithubPullRequest -apiurl $openPullRequest.url -AuthToken $AuthToken | Out-Null
      LogDebug "Open pull Request [ $($openPullRequest.url)] associate with branch [ $branchName ] in repo [ $RepoId ] has been closed."
    }
    catch
    {
      LogError "Close-GithubPullRequest failed with exception:`n$_"
      exit 1
    }
  }
}

LogDebug "Operating on Repo [ $RepoId ]"

try{
  $responses = Get-GitHubSourceReferences -RepoId $RepoId -Ref "heads/$BranchPrefix" -AuthToken $AuthToken
}
catch {
  LogError "Get-GitHubSourceReferences failed with exception:`n$_"
  exit 1
}

foreach ($res in $responses)
{
  if (!$res -or !$res.ref) {
    LogDebug "No branch returned from the branch prefix $BranchPrefix on $Repo. Skipping..."
    continue
  }
  if ($LastCommitOlderThan) {
    if (!$res.object -or !$res.object.url) {
      LogWarning "No commit url returned from response. Skipping... "
      continue
    }
    try {
      $commitDate = Get-GithubReferenceCommitDate -commitUrl $res.object.url -AuthToken $AuthToken
      if (!$commitDate) 
      {
        LogDebug "No last commit date found. Skipping."
        continue
      }
      if ($commitDate -gt $LastCommitOlderThan) {
        LogDebug "The branch $branch last commit date [ $commitDate ] is newer than the date $LastCommitOlderThan. Skipping."
        continue
      }
      
      LogDebug "Branch [ $branchName ] in repo [ $RepoId ] has a last commit date [ $commitDate ] that is older than $LastCommitOlderThan. "
    }
    catch {
      LogError "Get-GithubReferenceCommitDate failed with exception:`n$_"
      exit 1
    }
  } 
  
  $branch = $res.ref
  $branchName = $branch.Replace("refs/heads/","")
  $branchName -match $CentralPRRegex | Out-Null
  $pullRequestNumber = $Matches["PrNumber"]
  if ($pullRequestNumber) {
    RetrievePRAndClose -pullRequestNumber $pullRequestNumber
  }
  
  try {
    Remove-GitHubSourceReferences -RepoId $RepoId -Ref $branch -AuthToken $AuthToken
    LogDebug "The branch [ $branchName ] in [ $RepoId ] has been deleted."
  }
  catch {
    LogError "Remove-GitHubSourceReferences failed with exception:`n$_"
    exit 1
  }
}

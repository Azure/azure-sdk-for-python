# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'TestHelpers.ps1')

function New-MasterFixture {
    [pscustomobject]@{
        Calls = [Collections.Generic.List[object]]::new()
        NextId = 100
        DuplicateEndpoint = $false
        WrongYaml = $false
        FailedSecond = $false
        QueueError = $false
        Pending = $false
    }
}

function New-MasterInvoker {
    param($State)

    {
        param($Method, $Uri, $Headers, $Body, $TimeoutSeconds)
        $State.Calls.Add([pscustomobject]@{ Method = $Method; Uri = $Uri; Headers = $Headers; Body = $Body; Timeout = $TimeoutSeconds })
        if ($Method -eq 'Get' -and $Uri -match '/definitions/(?<id>\d+)\?') {
            $id = [int]$Matches.id
            $key = if ($id -eq 1 -or $State.DuplicateEndpoint) { 'a' * 32 } else { 'b' * 32 }
            $yaml = if ($State.WrongYaml) { 'sdk/ai/azure-ai-projects/tests.yml' } else { "sdk/ai/azure-ai-projects/pipelines/projects/foundry-$key.yml" }
            return [pscustomobject]@{ id = $id; revision = 3; queueStatus = 'enabled'; process = @{ yamlFilename = $yaml } }
        }
        if ($Method -eq 'Post') {
            $State.NextId++
            if ($State.QueueError -and $State.NextId -eq 101) { throw 'secret queue response' }
            return [pscustomobject]@{ id = $State.NextId }
        }
        if ($Method -eq 'Get' -and $Uri -match '/builds/(?<id>\d+)\?') {
            $id = [int]$Matches.id
            $result = if ($State.FailedSecond -and $id -eq 102) { 'failed' } else { 'succeeded' }
            return [pscustomobject]@{ id = $id; status = $(if ($State.Pending) { 'inProgress' } else { 'completed' }); result = $result }
        }
        throw 'Unexpected request.'
    }.GetNewClosure()
}

Describe 'Optional endpoint-only master' {
    It 'previews saved endpoint IDs without authentication, values, or required run-time inputs' {
        $targets = '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"}]'
        $plan = @(& $masterRunner -PipelinesJson $targets -RequestInvoker { throw 'No preview requests.' })
        $plan.Count | Should Be 1
        $plan[0].DefinitionId | Should Be 1
        $plan[0].TestId | Should BeNullOrEmpty
    }

    It 'queues all endpoint pipelines before polling and forwards no test profile or environment' {
        $state = New-MasterFixture
        $summary = Join-Path $TestDrive 'master-success.md'
        $result = @(& $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"},{"DefinitionId":2,"SourceBranch":"refs/heads/other"}]' `
            -SummaryPath $summary -Run -ConfirmRun -BearerToken ado-token -RequestInvoker (New-MasterInvoker $state))
        ($state.Calls.Method -join ',') | Should Be 'Get,Get,Post,Post,Get,Get'
        ($result.Result -join ',') | Should Be 'succeeded,succeeded'
        $queued = @($state.Calls | Where-Object { $_.Method -eq 'Post' })
        $queued[0].Body.resources.repositories.self.refName | Should Be 'refs/heads/topic'
        $queued[0].Body.variables | Should BeNullOrEmpty
        $queued[0].Body.templateParameters | Should BeNullOrEmpty
        @($state.Calls | Where-Object { $_.Timeout -lt 1 -or $_.Timeout -gt 60 }).Count | Should Be 0
        (Get-Content -LiteralPath $summary -Raw) | Should Not Match 'ado-token'
    }

    It 'rejects duplicate endpoints and a non-endpoint pipeline before any queue' {
        foreach ($failure in @('duplicate', 'wrong-yaml')) {
            $state = New-MasterFixture
            if ($failure -eq 'duplicate') { $state.DuplicateEndpoint = $true }
            if ($failure -eq 'wrong-yaml') { $state.WrongYaml = $true }
            $caught = $null
            try {
                & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"},{"DefinitionId":2,"SourceBranch":"refs/heads/topic"}]' `
                    -SummaryPath (Join-Path $TestDrive 'invalid.md') -Run -ConfirmRun -BearerToken ado-token `
                    -RequestInvoker (New-MasterInvoker $state)
            } catch { $caught = $_ }
            $caught | Should Not BeNullOrEmpty
            @($state.Calls | Where-Object { $_.Method -ne 'Get' }).Count | Should Be 0
        }
    }

    It 'requires approval and explicit unique target IDs with literal branches' {
        { & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"}]' -Run } | Should Throw 'ConfirmRun'
        { & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/*"}]' } | Should Throw 'unique positive'
        { & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"},{"DefinitionId":1,"SourceBranch":"refs/heads/topic"}]' } | Should Throw 'unique positive'
    }

    It 'reports partial failures without retrying a queue or canceling another endpoint run' {
        $state = New-MasterFixture
        $state.QueueError = $true
        $state.FailedSecond = $true
        $summary = Join-Path $TestDrive 'master-failed.md'
        {
            & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"},{"DefinitionId":2,"SourceBranch":"refs/heads/topic"}]' `
                -SummaryPath $summary -Run -ConfirmRun -BearerToken ado-token -RequestInvoker (New-MasterInvoker $state)
        } | Should Throw 'did not succeed'
        @($state.Calls | Where-Object { $_.Method -eq 'Post' }).Count | Should Be 2
        @($state.Calls | Where-Object { $_.Method -in @('Put', 'Patch', 'Delete') }).Count | Should Be 0
        $text = Get-Content -LiteralPath $summary -Raw
        $text | Should Match 'queue not confirmed'
        $text | Should Match 'failed'
        $text | Should Not Match 'secret queue response'
    }

    It 'uses a bounded timeout without sleeping in the unit test or canceling a child' {
        $state = New-MasterFixture
        $state.Pending = $true
        $time = [pscustomobject]@{ Value = [DateTimeOffset]'2026-01-01T00:00:00Z' }
        $clock = { $time.Value }.GetNewClosure()
        $wait = { param($Seconds) $time.Value = $time.Value.AddMinutes(2) }.GetNewClosure()
        $summary = Join-Path $TestDrive 'master-timeout.md'
        {
            & $masterRunner -PipelinesJson '[{"DefinitionId":1,"SourceBranch":"refs/heads/topic"}]' `
                -SummaryPath $summary -Run -ConfirmRun -BearerToken ado-token -Clock $clock -WaitInvoker $wait `
                -TimeoutMinutes 1 -RequestInvoker (New-MasterInvoker $state)
        } | Should Throw 'did not succeed'
        (Get-Content -LiteralPath $summary -Raw) | Should Match 'timed out \(child not canceled\)'
    }
}